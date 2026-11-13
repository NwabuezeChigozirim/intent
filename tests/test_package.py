#!/usr/bin/env python3
"""Structural checks for the plugin package itself."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
SKILLS = PACKAGE / "skills"
NAMED = re.compile(r"`([a-z][a-z0-9-]+)` skill\b|skills?[,:]? `([a-z][a-z0-9-]+)`(?:(?:,| and) `([a-z][a-z0-9-]+)`)?(?: and `([a-z][a-z0-9-]+)`)?")
SLASH = re.compile(r"`/([a-z][a-z0-9-]+)`")
LINK = re.compile(r"\]\((?!https?:|#|mailto:)([^)#\s]+)(?:#[^)]*)?\)")
# Skills of the governance plugin, and harness built-in commands.
EXTERNAL = {"govern", "correct", "govern-help", "adopt", "approve", "clear", "compact"}
# Backticked paths that look like slash commands.
PATHS = {"tmp", "settings"}
DROPPED = ("ask-matt", "setup-matt-pocock-skills", "Skill tool", "code-review", "/tdd", "/retro", "diagnosing-bugs", "/teach")


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def documents() -> list[Path]:
    return sorted(SKILLS.rglob("*.md"))


class PackageTests(unittest.TestCase):
    def test_manifest_points_at_the_skills(self) -> None:
        manifest = json.loads((PACKAGE / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertTrue((PACKAGE / manifest["skills"]).is_dir())
        self.assertNotIn("hooks", manifest)

    def test_every_skill_has_matching_frontmatter(self) -> None:
        for directory in skill_dirs():
            text = (directory / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), directory.name)
            front = text.split("---", 2)[1]
            name = re.search(r"^name:\s*(\S+)\s*$", front, re.MULTILINE)
            self.assertIsNotNone(name, directory.name)
            self.assertEqual(name.group(1), directory.name)
            self.assertRegex(front, r"(?m)^description:", directory.name)

    def test_every_referenced_skill_ships_or_is_known_external(self) -> None:
        present = {p.name for p in skill_dirs()}
        missing: dict[str, set[str]] = {}
        for path in documents():
            text = path.read_text(encoding="utf-8")
            names = {n for groups in NAMED.findall(text) for n in groups if n} | set(SLASH.findall(text))
            for name in names - present - EXTERNAL - PATHS:
                missing.setdefault(name, set()).add(path.relative_to(PACKAGE).as_posix())
        self.assertEqual(missing, {})

    def test_relative_links_resolve(self) -> None:
        broken = []
        for path in documents():
            fenced = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
            for target in LINK.findall(fenced):
                if "<" in target or not (path.parent / target).exists():
                    if "<" not in target:
                        broken.append(f"{path.relative_to(PACKAGE).as_posix()} -> {target}")
        self.assertEqual(broken, [])

    def test_no_reference_to_dropped_upstream_skills_remains(self) -> None:
        for path in documents():
            text = path.read_text(encoding="utf-8")
            for word in DROPPED:
                self.assertNotIn(word, text, f"{path.relative_to(PACKAGE).as_posix()}: {word}")

    def test_help_lists_every_skill(self) -> None:
        text = (SKILLS / "intent-help" / "SKILL.md").read_text(encoding="utf-8")
        missing = [p.name for p in skill_dirs() if f"](../{p.name}/SKILL.md)" not in text and p.name not in ("intent-help", "grilling")]
        self.assertEqual(missing, [])

    def test_setup_handles_a_governed_project(self) -> None:
        text = (SKILLS / "setup-intent" / "SKILL.md").read_text(encoding="utf-8")
        for glob in ("GLOSSARY.md", "**/GLOSSARY.md", "docs/adr/**", "docs/agents/**", ".scratch/**"):
            self.assertIn(f"`{glob}`", text)
        self.assertIn("you cannot edit that config yourself", text)

    def test_building_is_handed_to_governance(self) -> None:
        text = (SKILLS / "implement" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`govern` skill", text)
        self.assertIn("If the `governance` plugin is not installed, say so and stop.", text)


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.home, True)
        self.target = self.home / "plugins" / "local" / "intent"

    def install(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(PACKAGE / "scripts" / "install.py"), "--target", str(self.target)],
                              capture_output=True, text=True, check=False)

    def test_install_copies_the_plugin_without_tests(self) -> None:
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in (".cursor-plugin/plugin.json", "skills/grilling/SKILL.md", "LICENSE", "THIRD_PARTY_LICENSE-mattpocock-skills"):
            self.assertTrue((self.target / name).is_file(), name)
        self.assertFalse((self.target / "tests").exists())

    def test_reinstall_replaces_a_previous_install(self) -> None:
        self.install()
        (self.target / "stale.txt").write_text("old", encoding="utf-8")
        self.assertEqual(self.install().returncode, 0)
        self.assertFalse((self.target / "stale.txt").exists())

    def test_install_refuses_to_replace_an_unrelated_directory(self) -> None:
        self.target.mkdir(parents=True)
        (self.target / "notes.txt").write_text("mine", encoding="utf-8")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertTrue((self.target / "notes.txt").is_file())


if __name__ == "__main__":
    unittest.main()
