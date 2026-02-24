"""Tests for SkillRegistry."""

from pathlib import Path

import pytest

from spec_agent_skills.registry import SkillRegistry


class TestSkillRegistry:
    def test_load_skill(self, minimal_skill: Path):
        reg = SkillRegistry()
        skill = reg.load_skill(minimal_skill)
        assert skill.metadata.name == "my-skill"
        assert len(reg) == 1
        assert "my-skill" in reg

    def test_duplicate_skill_rejected(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        with pytest.raises(ValueError, match="already loaded"):
            reg.load_skill(minimal_skill)

    def test_load_skills_from_directory(self, skills_parent: Path):
        reg = SkillRegistry()
        loaded = reg.load_skills_from_directory(skills_parent)
        assert len(loaded) == 2
        assert "full-skill" in reg
        assert "my-skill" in reg

    def test_get_skill(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        assert reg.get_skill("my-skill") is not None
        assert reg.get_skill("nonexistent") is None

    def test_list_skills(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        metadata_list = reg.list_skills()
        assert len(metadata_list) == 1
        assert metadata_list[0].name == "my-skill"

    def test_activate_skill(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        instructions = reg.activate_skill("my-skill")
        assert "Do the thing step by step." in instructions
        assert reg.get_skill("my-skill").activated is True

    def test_activate_missing_skill(self):
        reg = SkillRegistry()
        with pytest.raises(KeyError, match="not found"):
            reg.activate_skill("nope")

    def test_read_resource(self, full_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(full_skill)
        content = reg.read_resource("full-skill", "scripts", "run.sh")
        assert "echo hello" in content

    def test_read_resource_missing_skill(self):
        reg = SkillRegistry()
        with pytest.raises(KeyError):
            reg.read_resource("nope", "scripts", "run.sh")

    def test_skill_names(self, skills_parent: Path):
        reg = SkillRegistry()
        reg.load_skills_from_directory(skills_parent)
        names = reg.skill_names
        assert "full-skill" in names
        assert "my-skill" in names

    def test_to_system_prompt(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        prompt = reg.to_system_prompt()
        assert "<available_skills>" in prompt
        assert "<name>my-skill</name>" in prompt

    def test_get_tools(self, minimal_skill: Path):
        reg = SkillRegistry()
        reg.load_skill(minimal_skill)
        tools = reg.get_tools()
        assert len(tools) == 3

    def test_empty_registry(self):
        reg = SkillRegistry()
        assert len(reg) == 0
        assert reg.list_skills() == []
        assert reg.to_system_prompt() == ""
