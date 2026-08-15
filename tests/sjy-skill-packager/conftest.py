import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "sjy-skill-packager"
    / "scripts"
    / "package_chatgpt_skill.py"
)

@pytest.fixture
def packager():
    spec = importlib.util.spec_from_file_location("sjy_skill_packager", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

@pytest.fixture
def make_skill():
    def _make(path: Path, name: str, body: str = "# Test\n") -> Path:
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill for packaging.\n---\n\n{body}",
            encoding="utf-8",
        )
        return path
    return _make
