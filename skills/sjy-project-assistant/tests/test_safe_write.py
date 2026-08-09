from pathlib import Path

import pytest

from scripts.safe_write import (
    ManagedBlockError,
    atomic_write_text,
    replace_managed_block,
)


BEGIN = "<!-- BEGIN SJY PROJECT ASSISTANT GOVERNANCE v1 -->"
END = "<!-- END SJY PROJECT ASSISTANT GOVERNANCE v1 -->"
BLOCK = f"{BEGIN}\nmanaged\n{END}"


def test_inserts_block_without_destroying_existing_text():
    existing = "# Existing Rules\n\nKeep this.\n"

    result = replace_managed_block(existing, BLOCK, BEGIN, END)

    assert "# Existing Rules" in result
    assert "Keep this." in result
    assert BLOCK in result


def test_replaces_existing_managed_block_and_preserves_surrounding_text():
    existing = f"before\n\n{BEGIN}\nold\n{END}\n\nafter\n"

    result = replace_managed_block(existing, BLOCK, BEGIN, END)

    assert result.count(BEGIN) == 1
    assert result.count(END) == 1
    assert "old" not in result
    assert result.startswith("before")
    assert result.rstrip().endswith("after")


def test_second_application_is_idempotent():
    first = replace_managed_block("before\n", BLOCK, BEGIN, END)
    second = replace_managed_block(first, BLOCK, BEGIN, END)

    assert second == first


def test_refuses_malformed_single_marker():
    with pytest.raises(ManagedBlockError):
        replace_managed_block(f"before\n{BEGIN}\nold\n", BLOCK, BEGIN, END)


def test_refuses_reversed_managed_markers():
    existing = f"{END}\nold\n{BEGIN}\n"

    with pytest.raises(ManagedBlockError):
        replace_managed_block(existing, BLOCK, BEGIN, END)


def test_atomic_write_creates_optional_backup(tmp_path: Path):
    target = tmp_path / "AGENTS.md"
    target.write_text("old\n", encoding="utf-8")

    atomic_write_text(target, "new\n", backup=True)

    assert target.read_text(encoding="utf-8") == "new\n"
    assert target.with_suffix(target.suffix + ".bak").read_text(encoding="utf-8") == "old\n"


def test_atomic_write_refuses_target_outside_intended_root(tmp_path: Path):
    intended_root = tmp_path / "repository"
    intended_root.mkdir()
    outside_target = tmp_path / "outside" / "AGENTS.md"

    with pytest.raises(ValueError, match="outside intended root"):
        atomic_write_text(outside_target, "new\n", root=intended_root)

    assert not outside_target.exists()


def test_atomic_write_refuses_reported_symlink_leaf(tmp_path: Path, monkeypatch):
    target = tmp_path / "AGENTS.md"
    target.write_text("old\n", encoding="utf-8")

    monkeypatch.setattr(Path, "is_symlink", lambda path: path == target)

    with pytest.raises(ValueError, match="symbolic link"):
        atomic_write_text(target, "new\n")

    assert target.read_text(encoding="utf-8") == "old\n"


def test_atomic_write_refuses_symlink_leaf_without_root(tmp_path: Path):
    referent = tmp_path / "outside.md"
    referent.write_text("outside\n", encoding="utf-8")
    target = tmp_path / "AGENTS.md"
    _symlink_or_skip(target, referent)

    with pytest.raises(ValueError, match="symbolic link"):
        atomic_write_text(target, "new\n")

    assert target.is_symlink()
    assert referent.read_text(encoding="utf-8") == "outside\n"


def test_atomic_write_refuses_symlink_leaf_to_in_root_referent(tmp_path: Path):
    intended_root = tmp_path / "repository"
    intended_root.mkdir()
    referent = intended_root / "existing.md"
    referent.write_text("inside\n", encoding="utf-8")
    target = intended_root / "AGENTS.md"
    _symlink_or_skip(target, referent)

    with pytest.raises(ValueError, match="symbolic link"):
        atomic_write_text(target, "new\n", root=intended_root)

    assert target.is_symlink()
    assert referent.read_text(encoding="utf-8") == "inside\n"


def test_atomic_write_refuses_symlink_leaf_to_out_of_root_referent(tmp_path: Path):
    intended_root = tmp_path / "repository"
    intended_root.mkdir()
    referent = tmp_path / "outside.md"
    referent.write_text("outside\n", encoding="utf-8")
    target = intended_root / "AGENTS.md"
    _symlink_or_skip(target, referent)

    with pytest.raises(ValueError, match="symbolic link"):
        atomic_write_text(target, "new\n", root=intended_root)

    assert target.is_symlink()
    assert referent.read_text(encoding="utf-8") == "outside\n"


def _symlink_or_skip(link: Path, referent: Path) -> None:
    try:
        link.symlink_to(referent)
    except (NotImplementedError, OSError) as error:
        pytest.skip(f"Symbolic links are unavailable: {error}")


def test_refuses_multiple_managed_blocks():
    existing = f"{BLOCK}\n{BLOCK}\n"

    with pytest.raises(ManagedBlockError):
        replace_managed_block(existing, BLOCK, BEGIN, END)
