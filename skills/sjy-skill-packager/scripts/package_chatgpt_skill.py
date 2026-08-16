#!/usr/bin/env python3
"""Validate and package an installed Agent Skill for ChatGPT Web."""

# The validated Task 1-5 core stays isolated from Task 6 orchestration so the
# CLI layer can remain small and reviewable. Execute it in this module's
# namespace so monkeypatching and public function globals retain legacy behavior.
from pathlib import Path as _BootstrapPath

_CORE_PATH = _BootstrapPath(__file__).with_name("_packager_core.py")
exec(compile(_CORE_PATH.read_text(encoding="utf-8"), str(_CORE_PATH), "exec"), globals(), globals())

del _BootstrapPath

import argparse
import json
import sys
import tempfile


def _status_from_issues(issues: list[Issue]) -> PackageStatus:
    if any(issue.status is PackageStatus.FAIL for issue in issues):
        return PackageStatus.FAIL
    if any(issue.status is PackageStatus.AMBIGUOUS for issue in issues):
        return PackageStatus.AMBIGUOUS
    if any(issue.status is PackageStatus.NEEDS_ADAPTATION for issue in issues):
        return PackageStatus.NEEDS_ADAPTATION
    return PackageStatus.SUCCESS


def package_skill(source: str, output_dir: Optional[Path], cwd: Path, home: Path) -> PackageResult:
    cwd, home = cwd.resolve(), home.resolve()
    try:
        resolution = resolve_skill(source, cwd, home)
    except Exception as exc:
        return PackageResult(
            PackageStatus.FAIL,
            Path(source).name or source,
            issues=[_fail("RESOLUTION_ERROR", f"Failed to resolve Skill: {exc}")],
        )

    candidate_paths = [str(candidate.path) for candidate in resolution.candidates]
    skill_name = resolution.path.name if resolution.path is not None else (Path(source).name or source)
    if resolution.issues:
        return PackageResult(
            _status_from_issues(resolution.issues),
            skill_name,
            source=str(resolution.path) if resolution.path is not None else None,
            notices=list(resolution.notices),
            issues=list(resolution.issues),
            candidates=candidate_paths,
        )
    if resolution.path is None:
        return PackageResult(
            PackageStatus.FAIL,
            skill_name,
            notices=list(resolution.notices),
            issues=[_fail("RESOLUTION_EMPTY", "Skill resolution produced no source path.")],
            candidates=candidate_paths,
        )

    skill_path = resolution.path.resolve()
    issues: list[Issue] = []
    for validator in (validate_skill, validate_openai_metadata, validate_package_boundary):
        try:
            issues.extend(validator(skill_path))
        except Exception as exc:
            issues.append(_fail("VALIDATION_ERROR", f"Validation failed unexpectedly: {exc}", skill_path))
    status = _status_from_issues(issues)
    if status is not PackageStatus.SUCCESS:
        return PackageResult(
            status,
            skill_path.name,
            source=str(skill_path),
            notices=list(resolution.notices),
            issues=issues,
            candidates=candidate_paths,
        )

    destination = output_dir if output_dir is not None else cwd / "dist"
    if not destination.is_absolute():
        destination = cwd / destination
    destination = destination.resolve(strict=False)
    final_path = (destination / f"{skill_path.name}-chatgpt.zip").resolve(strict=False)
    if is_within(destination, skill_path) or is_within(final_path, skill_path):
        issue = _fail(
            "OUTPUT_INSIDE_SOURCE",
            "Output directory and archive must be outside the source Skill directory.",
            destination,
        )
        return PackageResult(
            PackageStatus.FAIL,
            skill_path.name,
            source=str(skill_path),
            notices=list(resolution.notices),
            issues=[issue],
            candidates=candidate_paths,
        )

    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return PackageResult(
            PackageStatus.FAIL,
            skill_path.name,
            source=str(skill_path),
            notices=list(resolution.notices),
            issues=[_fail("OUTPUT_DIRECTORY_ERROR", f"Cannot create output directory: {exc}", destination)],
            candidates=candidate_paths,
        )

    temp_path: Optional[Path] = None
    try:
        fd, raw_temp = tempfile.mkstemp(
            prefix=f".{skill_path.name}-", suffix=".tmp.zip", dir=destination
        )
        os.close(fd)
        temp_path = Path(raw_temp)
        build_zip(skill_path, temp_path)
        verify_issues = verify_zip(temp_path, skill_path)
        if verify_issues:
            return PackageResult(
                _status_from_issues(verify_issues),
                skill_path.name,
                source=str(skill_path),
                notices=list(resolution.notices),
                issues=verify_issues,
                candidates=candidate_paths,
            )
        try:
            os.replace(temp_path, final_path)
        except OSError as exc:
            return PackageResult(
                PackageStatus.FAIL,
                skill_path.name,
                source=str(skill_path),
                notices=list(resolution.notices),
                issues=[_fail("ATOMIC_REPLACE_ERROR", f"Cannot atomically replace final archive: {exc}", final_path)],
                candidates=candidate_paths,
            )
        temp_path = None
        return PackageResult(
            PackageStatus.SUCCESS,
            skill_path.name,
            source=str(skill_path),
            artifact=str(final_path),
            notices=list(resolution.notices),
            candidates=candidate_paths,
        )
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        return PackageResult(
            PackageStatus.FAIL,
            skill_path.name,
            source=str(skill_path),
            notices=list(resolution.notices),
            issues=[_fail("PACKAGE_BUILD_ERROR", f"Cannot build temporary archive: {exc}", temp_path or destination)],
            candidates=candidate_paths,
        )
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and package a local Agent Skill for ChatGPT Web upload."
    )
    parser.add_argument("source", help="Installed Skill name or explicit Skill directory path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for <skill-name>-chatgpt.zip (default: ./dist)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit exactly one JSON result object on stdout"
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = package_skill(args.source, args.output_dir, Path.cwd(), Path.home())
    if args.json:
        print(json.dumps(result_to_dict(result), ensure_ascii=False))
    else:
        print(f"{result.status.value}: {result.skill}")
        if result.artifact:
            print(f"Artifact: {result.artifact}")
        for notice in result.notices:
            print(f"Notice: {notice}")
        for issue in result.issues:
            suffix = f" ({issue.path})" if issue.path else ""
            print(f"{issue.status.value} {issue.code}: {issue.message}{suffix}")
        if result.status is PackageStatus.AMBIGUOUS:
            for candidate in result.candidates:
                print(f"Candidate: {candidate}")

    return {
        PackageStatus.SUCCESS: EXIT_SUCCESS,
        PackageStatus.FAIL: EXIT_FAIL,
        PackageStatus.NEEDS_ADAPTATION: EXIT_NEEDS_ADAPTATION,
        PackageStatus.AMBIGUOUS: EXIT_AMBIGUOUS,
    }[result.status]


if __name__ == "__main__":
    sys.exit(main())
