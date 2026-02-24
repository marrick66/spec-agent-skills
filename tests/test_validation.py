"""Tests for validation logic."""

from pathlib import Path

import pytest

from spec_agent_skills.parser import parse_skill
from spec_agent_skills.validation import (
    validate_name_matches_directory,
    validate_resource_path,
    validate_skill_directory,
)


class TestValidateSkillDirectory:
    def test_valid_directory(self, minimal_skill: Path):
        validate_skill_directory(minimal_skill)

    def test_nonexistent_path(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="not found"):
            validate_skill_directory(tmp_path / "nope")

    def test_not_a_directory(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("hi")
        with pytest.raises(ValueError, match="not a directory"):
            validate_skill_directory(f)

    def test_no_skill_md(self, tmp_path: Path):
        d = tmp_path / "empty"
        d.mkdir()
        with pytest.raises(FileNotFoundError, match="SKILL.md"):
            validate_skill_directory(d)


class TestValidateNameMatchesDirectory:
    def test_match(self):
        validate_name_matches_directory("my-skill", "my-skill")

    def test_mismatch(self):
        with pytest.raises(ValueError, match="must match"):
            validate_name_matches_directory("skill-a", "skill-b")


class TestValidateResourcePath:
    def test_valid_resource(self, full_skill: Path):
        skill = parse_skill(full_skill)
        path = validate_resource_path(skill, "scripts", "run.sh")
        assert path.is_file()

    def test_invalid_resource_type(self, full_skill: Path):
        skill = parse_skill(full_skill)
        with pytest.raises(ValueError, match="Invalid resource type"):
            validate_resource_path(skill, "invalid", "file.txt")

    def test_no_resource_dir(self, minimal_skill: Path):
        skill = parse_skill(minimal_skill)
        with pytest.raises(FileNotFoundError, match="no scripts"):
            validate_resource_path(skill, "scripts", "run.sh")

    def test_path_traversal(self, full_skill: Path):
        skill = parse_skill(full_skill)
        with pytest.raises(ValueError, match="traversal"):
            validate_resource_path(skill, "scripts", "../../etc/passwd")

    def test_nonexistent_file(self, full_skill: Path):
        skill = parse_skill(full_skill)
        with pytest.raises(FileNotFoundError, match="not found"):
            validate_resource_path(skill, "scripts", "missing.sh")
