from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest


def archive_names(path: Path):
    with ZipFile(path, "r") as archive:
        return archive.namelist()


def test_build_zip_preserves_runtime_and_unknown_files_but_excludes_junk(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    keep = {
        "scripts/run.py": b"print('ok')\n",
        "references/info.md": b"# Info\n",
        "assets/icon.txt": b"icon",
        "docs/keep.md": b"docs",
        "examples/keep.txt": b"example",
        "custom/keep.bin": b"\x00\x01",
        "tests/keep.py": b"assert True\n",
        "sub/evals/keep.md": b"nested evals are not root evals",
    }
    for rel, data in keep.items():
        path = skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    drop = {
        "__pycache__/drop.pyc": b"x",
        "node_modules/drop.txt": b"x",
        ".git/config": b"x",
        ".pytest_cache/drop": b"x",
        ".DS_Store": b"x",
        "evals/drop.md": b"x",
        "cache/file.pyc": b"x",
    }
    for rel, data in drop.items():
        path = skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    output = tmp_path / "demo.zip"
    packager.build_zip(skill, output)
    names = archive_names(output)
    assert "demo/SKILL.md" in names
    for rel in keep:
        assert f"demo/{rel}" in names
    for rel in drop:
        assert f"demo/{rel}" not in names
    assert all(name.startswith("demo/") for name in names)
    assert all("\\" not in name for name in names)


def test_zip_entries_use_fixed_metadata(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    output = tmp_path / "demo.zip"
    packager.build_zip(skill, output)
    with ZipFile(output, "r") as archive:
        info = archive.getinfo("demo/SKILL.md")
    assert info.date_time == (1980, 1, 1, 0, 0, 0)
    assert info.compress_type == ZIP_DEFLATED
    assert info.create_system == 3
    assert (info.external_attr >> 16) & 0o777 == 0o644


def test_repeated_builds_are_byte_identical(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / "references").mkdir()
    (skill / "references" / "a.md").write_text("same", encoding="utf-8")
    one = tmp_path / "one.zip"
    two = tmp_path / "two.zip"
    packager.build_zip(skill, one)
    packager.build_zip(skill, two)
    assert one.read_bytes() == two.read_bytes()


def test_build_zip_does_not_follow_nested_symlink(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    link = skill / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    with pytest.raises(ValueError):
        packager.build_zip(skill, tmp_path / "demo.zip")


def test_verify_zip_accepts_valid_archive(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    output = tmp_path / "demo.zip"
    packager.build_zip(skill, output)
    assert packager.verify_zip(output, skill) == []


def write_custom_zip(path: Path, entries: dict[str, bytes]):
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)


def test_verify_zip_rejects_path_traversal(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": (skill / "SKILL.md").read_bytes(), "demo/../evil.txt": b"x"})
    assert "ZIP_UNSAFE_PATH" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_rejects_absolute_path(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": (skill / "SKILL.md").read_bytes(), "/evil.txt": b"x"})
    assert "ZIP_UNSAFE_PATH" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_rejects_wrong_top_level(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"other/SKILL.md": (skill / "SKILL.md").read_bytes()})
    assert "ZIP_WRONG_TOP_LEVEL" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_requires_skill_md(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/other.txt": b"x"})
    assert "ZIP_SKILL_MD_MISSING" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_detects_source_byte_mismatch(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": b"changed"})
    assert "ZIP_MANIFEST_MISMATCH" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_detects_unexpected_file(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": (skill / "SKILL.md").read_bytes(), "demo/unexpected.txt": b"x"})
    assert "ZIP_MANIFEST_MISMATCH" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_detects_excluded_file_leak(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": (skill / "SKILL.md").read_bytes(), "demo/.DS_Store": b"x"})
    assert "ZIP_EXCLUDED_FILE_PRESENT" in {i.code for i in packager.verify_zip(path, skill)}


def test_verify_zip_handles_invalid_zip_bytes(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    path.write_bytes(b"not a zip")
    assert "ZIP_INVALID" in {i.code for i in packager.verify_zip(path, skill)}


def test_source_mtime_and_mode_do_not_change_archive_bytes(packager, make_skill, tmp_path):
    import os
    skill = make_skill(tmp_path / "demo", "demo")
    source = skill / "SKILL.md"
    one = tmp_path / "one.zip"
    two = tmp_path / "two.zip"
    packager.build_zip(skill, one)
    os.utime(source, (1000000000, 1000000000))
    try:
        source.chmod(0o600)
    except OSError:
        pass
    packager.build_zip(skill, two)
    assert one.read_bytes() == two.read_bytes()


def test_verify_zip_rejects_windows_drive_like_path(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    path = tmp_path / "bad.zip"
    write_custom_zip(path, {"demo/SKILL.md": (skill / "SKILL.md").read_bytes(), "C:/evil.txt": b"x"})
    assert "ZIP_UNSAFE_PATH" in {i.code for i in packager.verify_zip(path, skill)}
