from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


class ManagedBlockError(ValueError):
    pass


def replace_managed_block(
    existing: str,
    block: str,
    begin_marker: str,
    end_marker: str,
) -> str:
    begin_count = existing.count(begin_marker)
    end_count = existing.count(end_marker)

    if begin_count != end_count:
        raise ManagedBlockError("Managed block markers are incomplete")
    if begin_count > 1:
        raise ManagedBlockError("Multiple managed blocks are ambiguous")

    normalized_block = block.strip() + "\n"

    if begin_count == 0:
        if not existing:
            return normalized_block
        separator = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
        return existing + separator + normalized_block

    begin = existing.index(begin_marker)
    end_start = existing.index(end_marker)
    if end_start < begin:
        raise ManagedBlockError("Managed block markers are out of order")
    end = end_start + len(end_marker)

    replacement = normalized_block.rstrip("\n")
    result = existing[:begin] + replacement + existing[end:]
    if existing.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def atomic_write_text(
    path: Path,
    content: str,
    *,
    backup: bool = False,
    root: Path | None = None,
) -> None:
    path = path.parent.resolve() / path.name
    if path.is_symlink():
        raise ValueError(f"Write target is a symbolic link: {path}")

    if root is not None:
        intended_root = root.resolve()
        try:
            path.relative_to(intended_root)
        except ValueError as error:
            raise ValueError(f"Write target is outside intended root: {path}") from error

    path.parent.mkdir(parents=True, exist_ok=True)

    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup_path)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        finally:
            raise
