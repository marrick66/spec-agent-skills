"""Tests for SKILL.md parsing."""

from pathlib import Path

import pytest

from spec_agent_skills.parser import parse_skill, _split_frontmatter


class TestSplitFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\nname: test\n---\nBody content."
        fm, body = _split_frontmatter(content)
        assert fm == {"name": "test"}
        assert body == "Body content."

    def test_missing_opening_delimiter(self):
        with pytest.raises(ValueError, match="must start with"):
            _split_frontmatter("name: test\n---\nBody")

    def test_missing_closing_delimiter(self):
        with pytest.raises(ValueError, match="delimited by ---"):
            _split_frontmatter("---\nname: test\n")

    def test_empty_body(self):
        fm, body = _split_frontmatter("---\nname: test\n---\n")
        assert fm == {"name": "test"}
        assert body == ""

    def test_non_dict_frontmatter(self):
        with pytest.raises(ValueError, match="YAML mapping"):
            _split_frontmatter("---\n- item1\n- item2\n---\nBody")


class TestParseSkill:
    def test_minimal_skill(self, minimal_skill: Path):
        skill = parse_skill(minimal_skill)
        assert skill.metadata.name == "my-skill"
        assert skill.metadata.description == "A test skill for unit testing."
        assert "Do the thing step by step." in skill.instructions
        assert skill.activated is False

    def test_full_skill(self, full_skill: Path):
        skill = parse_skill(full_skill)
        assert skill.metadata.name == "full-skill"
        assert skill.metadata.license == "Apache-2.0"
        assert skill.metadata.compatibility == "Requires Python 3.13+"
        assert skill.metadata.metadata == {"author": "test-org", "version": "1.0"}
        assert skill.metadata.allowed_tools == ["Bash(git:*)", "Read"]

    def test_resource_discovery(self, full_skill: Path):
        skill = parse_skill(full_skill)
        assert skill.resources.scripts_dir is not None
        assert skill.resources.references_dir is not None
        assert skill.resources.assets_dir is not None

    def test_no_resources(self, minimal_skill: Path):
        skill = parse_skill(minimal_skill)
        assert skill.resources.scripts_dir is None
        assert skill.resources.references_dir is None
        assert skill.resources.assets_dir is None

    def test_list_resource_files(self, full_skill: Path):
        skill = parse_skill(full_skill)
        assert "run.sh" in skill.resources.list_files("scripts")
        assert "REFERENCE.md" in skill.resources.list_files("references")
        assert "template.txt" in skill.resources.list_files("assets")

    def test_missing_directory(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            parse_skill(tmp_path / "nonexistent")

    def test_missing_skill_md(self, tmp_path: Path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="SKILL.md"):
            parse_skill(empty_dir)

    def test_name_directory_mismatch(self, tmp_path: Path):
        skill_dir = tmp_path / "wrong-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: correct-name\ndescription: Test.\n---\nBody\n"
        )
        with pytest.raises(ValueError, match="must match directory name"):
            parse_skill(skill_dir)
