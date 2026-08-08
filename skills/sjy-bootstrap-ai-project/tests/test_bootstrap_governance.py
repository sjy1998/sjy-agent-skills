from __future__ import annotations

import codecs
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "bootstrap_governance.py"
AGENTS_ASSET = SKILL_ROOT / "assets" / "agents-managed.md"
CLAUDE_ASSET = SKILL_ROOT / "assets" / "claude-managed.md"
VERSION = "1.0.0"


def load_bootstrap():
    if not SCRIPT_PATH.exists():
        raise AssertionError(
            "bootstrap_governance.py is missing; the Skill package is incomplete"
        )
    spec = importlib.util.spec_from_file_location("bootstrap_governance", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_fixture_body(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return normalized + "\n"


def fixture_block(body: str, version: str = VERSION, eol: str = "\n") -> str:
    canonical = canonical_fixture_body(body)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    lines = [
        f"<!-- BEGIN SJY-AI-ENGINEERING-MANAGED version={version} sha256={digest} -->",
        canonical.rstrip("\n"),
        "<!-- END SJY-AI-ENGINEERING-MANAGED -->",
    ]
    return eol.join(lines) + eol


class BootstrapGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.bootstrap = load_bootstrap()

    def test_canonical_body_normalizes_newlines_and_one_terminal_lf(self):
        self.assertEqual("alpha\nbeta\n", self.bootstrap.canonical_body("alpha\r\nbeta\r\n\r\n"))

    def test_content_hash_uses_utf8_canonical_body(self):
        expected = hashlib.sha256(b"alpha\nbeta\n").hexdigest()
        self.assertEqual(expected, self.bootstrap.content_hash("alpha\r\nbeta"))

    def test_inspect_uninitialized_reports_ready_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.bootstrap.inspect_repository(root)

            self.assertEqual("UNINITIALIZED", result["state"])
            self.assertEqual("READY_TO_INITIALIZE", result["result"])
            self.assertEqual(["AGENTS.md"], result["targets"])
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("NOT_A_GIT_REPOSITORY", result["diagnostics"])

    def test_initialize_creates_targets_and_then_inspects_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.bootstrap.initialize_repository(root, include_claude=True)

            self.assertEqual("INITIALIZED", result["result"])
            self.assertEqual(["AGENTS.md", "CLAUDE.md"], result["changed_files"])
            inspected = self.bootstrap.inspect_repository(root, include_claude=True)
            self.assertEqual("CURRENT", inspected["state"])
            self.assertEqual("NO_CHANGES", inspected["result"])

    def test_initialize_preserves_existing_content_bom_and_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = codecs.BOM_UTF8 + b"# Team Rules\r\n\r\nKeep this.\r\n"
            (root / "AGENTS.md").write_bytes(original)

            result = self.bootstrap.initialize_repository(root)
            written = (root / "AGENTS.md").read_bytes()

            self.assertEqual("INITIALIZED", result["result"])
            self.assertTrue(written.startswith(original))
            self.assertTrue(written.startswith(codecs.BOM_UTF8))
            self.assertNotIn(b"\n", written.replace(b"\r\n", b""))

    def test_current_rerun_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.bootstrap.initialize_repository(root)
            before = (root / "AGENTS.md").read_bytes()

            result = self.bootstrap.initialize_repository(root)

            self.assertEqual("NO_CHANGES", result["result"])
            self.assertEqual([], result["changed_files"])
            self.assertEqual(before, (root / "AGENTS.md").read_bytes())

    def test_mismatched_installed_versions_are_partial_before_upgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(fixture_block("agents old", "1.0.0"), encoding="utf-8")
            (root / "CLAUDE.md").write_text(fixture_block("claude older", "0.9.0"), encoding="utf-8")

            result = self.bootstrap.inspect_repository(root)

            self.assertEqual("PARTIAL", result["state"])
            self.assertEqual("PARTIAL", result["result"])

    def test_same_old_version_is_upgrade_available_but_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = fixture_block("agents old", "0.9.0")
            claude = fixture_block("claude old", "0.9.0")
            (root / "AGENTS.md").write_text(agents, encoding="utf-8")
            (root / "CLAUDE.md").write_text(claude, encoding="utf-8")

            result = self.bootstrap.inspect_repository(root)

            self.assertEqual("UPGRADE_AVAILABLE", result["state"])
            self.assertEqual("UPGRADE_AVAILABLE", result["result"])
            self.assertEqual(agents, (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_newer_installed_version_is_conflict_and_upgrade_never_downgrades(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = fixture_block("newer body", "2.0.0")
            (root / "AGENTS.md").write_text(original, encoding="utf-8")

            inspected = self.bootstrap.inspect_repository(root)
            upgraded = self.bootstrap.upgrade_repository(root)

            self.assertEqual("CONFLICT", inspected["state"])
            self.assertIn("NEWER_VERSION_INSTALLED:AGENTS.md", inspected["diagnostics"])
            self.assertEqual("CONFLICT", upgraded["result"])
            self.assertEqual(original, (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_same_version_modified_managed_body_is_drifted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                fixture_block("manually changed body", VERSION), encoding="utf-8"
            )

            result = self.bootstrap.inspect_repository(root)

            self.assertEqual("DRIFTED", result["state"])
            self.assertEqual("DRIFT_DETECTED", result["result"])

    def test_invalid_or_duplicate_markers_are_malformed(self):
        cases = {
            "missing end": "<!-- BEGIN SJY-AI-ENGINEERING-MANAGED version=1.0.0 sha256=abc -->\nbody\n",
            "duplicate": fixture_block("one") + fixture_block("two"),
        }
        for label, content in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "AGENTS.md").write_text(content, encoding="utf-8")
                result = self.bootstrap.inspect_repository(root)
                self.assertEqual("MALFORMED", result["state"])
                self.assertEqual("MALFORMED", result["result"])

    def test_invalid_semver_and_corrupt_marker_like_line_are_malformed_and_block_initialize(self):
        cases = {
            "invalid semver": fixture_block("body", "one.point.zero"),
            "corrupt begin": "<!-- BEGIN SJY-AI-ENGINEERING-MANAGED version=1.0.0 -->\nbody\n",
        }
        for label, content in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                target = root / "AGENTS.md"
                target.write_text(content, encoding="utf-8")

                inspected = self.bootstrap.inspect_repository(root)
                initialized = self.bootstrap.initialize_repository(root)

                self.assertEqual("MALFORMED", inspected["state"])
                self.assertEqual("MALFORMED", initialized["result"])
                self.assertEqual(content, target.read_text(encoding="utf-8"))

    def test_read_only_target_is_refused_during_inspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "AGENTS.md"
            target.write_text("team rules", encoding="utf-8")
            target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            try:
                result = self.bootstrap.inspect_repository(root)
            finally:
                target.chmod(stat.S_IWUSR | stat.S_IRUSR)

            self.assertEqual("CONFLICT", result["state"])
            self.assertIn("READ_ONLY_TARGET_REFUSED:AGENTS.md", result["diagnostics"])

    def test_initialize_preserves_missing_terminal_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = b"# Team Rules"
            target = root / "AGENTS.md"
            target.write_bytes(original)

            result = self.bootstrap.initialize_repository(root)
            written = target.read_bytes()

            self.assertEqual("INITIALIZED", result["result"])
            self.assertTrue(written.startswith(original))
            self.assertFalse(written.endswith((b"\n", b"\r")))

    def test_mutation_rejects_failed_postcondition_and_preserves_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = b"# Team Rules\n"
            target = root / "AGENTS.md"
            target.write_bytes(original)

            with mock.patch.object(self.bootstrap, "apply_changes", lambda changes: None):
                with self.assertRaises(self.bootstrap.WriteTransactionError):
                    self.bootstrap.initialize_repository(root)

            self.assertEqual(original, target.read_bytes())

    def test_inspect_discovers_nearest_git_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp) / "repository"
            nested = repository / "packages" / "app"
            (repository / ".git").mkdir(parents=True)
            nested.mkdir(parents=True)

            result = self.bootstrap.inspect_repository(nested)

            self.assertEqual(str(repository.resolve()), result["root"])
            self.assertFalse((nested / "AGENTS.md").exists())
            self.assertNotIn("NOT_A_GIT_REPOSITORY", result["diagnostics"])

    def test_v1_upgrade_reports_available_without_migrating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prefix = "# Custom before\n\n"
            suffix = "\n# Custom after\n"
            (root / "AGENTS.md").write_text(
                prefix + fixture_block("old body", "0.9.0") + suffix,
                encoding="utf-8",
            )

            result = self.bootstrap.upgrade_repository(root)
            written = (root / "AGENTS.md").read_text(encoding="utf-8")

            self.assertEqual("UPGRADE_AVAILABLE", result["result"])
            self.assertEqual(prefix + fixture_block("old body", "0.9.0") + suffix, written)
            self.assertEqual("UPGRADE_AVAILABLE", self.bootstrap.inspect_repository(root)["state"])

    def test_equivalent_directories_are_reported_without_creating_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "architecture-decisions").mkdir(parents=True)
            (root / "docs" / "code-reviews").mkdir(parents=True)

            result = self.bootstrap.inspect_repository(root)

            self.assertEqual(
                {
                    "decisions": "docs/architecture-decisions",
                    "reviews": "docs/code-reviews",
                },
                result["equivalent_directories"],
            )
            self.assertFalse((root / "docs" / "decisions").exists())
            self.assertFalse((root / "docs" / "reviews").exists())

    def test_symlinked_target_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real-agents.md"
            real.write_text("custom", encoding="utf-8")
            try:
                os.symlink(real, root / "AGENTS.md")
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            result = self.bootstrap.inspect_repository(root)

            self.assertEqual("MALFORMED", result["state"])
            self.assertIn("SYMLINK_TARGET_REFUSED:AGENTS.md", result["diagnostics"])

    def test_apply_changes_rolls_back_files_after_replace_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.md"
            second = root / "second.md"
            first.write_bytes(b"first-original")
            second.write_bytes(b"second-original")
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated replacement failure")
                os.replace(source, destination)

            with self.assertRaises(self.bootstrap.WriteTransactionError):
                self.bootstrap.apply_changes(
                    {first: b"first-new", second: b"second-new"},
                    replace_fn=fail_second_replace,
                )

            self.assertEqual(b"first-original", first.read_bytes())
            self.assertEqual(b"second-original", second.read_bytes())

    def test_apply_changes_restores_original_mode_after_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.md"
            second = root / "second.md"
            first.write_bytes(b"first-original")
            second.write_bytes(b"second-original")
            first.chmod(0o644)
            original_mode = stat.S_IMODE(first.stat().st_mode)
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated replacement failure")
                os.replace(source, destination)

            with self.assertRaises(self.bootstrap.WriteTransactionError):
                self.bootstrap.apply_changes(
                    {first: b"first-new", second: b"second-new"},
                    replace_fn=fail_second_replace,
                )

            self.assertEqual(original_mode, stat.S_IMODE(first.stat().st_mode))

    def test_cli_blocked_operation_exits_two_with_complete_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                "<!-- BEGIN SJY-AI-ENGINEERING-MANAGED version=1.0.0 -->\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "initialize", "--root", tmp, "--json"],
                check=False,
                capture_output=True,
                text=True,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(2, completed.returncode)
            self.assertEqual("MALFORMED", payload["state"])
            self.assertEqual([], payload["changed_files"])
            self.assertIn("root", payload)
            self.assertIn("targets", payload)

    def test_assets_contain_required_durable_governance_boundaries(self):
        agents = AGENTS_ASSET.read_text(encoding="utf-8")
        claude = CLAUDE_ASSET.read_text(encoding="utf-8")

        for text in (
            "External systems are authoritative within their own domains",
            "Secrets must not be written to the repository",
            "Governance / Architecture     => Codex",
            "Implementation                => Claude",
            "Draft | Approved | Superseded",
            "current approved Spec",
        ):
            self.assertIn(text, agents)
        for text in ("recent commits", "repeated verification failure", "cannot reliably determine correctness"):
            self.assertIn(text, claude)

    def test_cli_inspect_json_uses_stable_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "inspect",
                    "--root",
                    tmp,
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("UNINITIALIZED", payload["state"])
            self.assertEqual("READY_TO_INITIALIZE", payload["result"])


if __name__ == "__main__":
    unittest.main()
