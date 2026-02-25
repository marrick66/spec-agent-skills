"""Tests for Strands agent tools."""

from pathlib import Path

from agent_skills.registry import FileSystemSkillRegistry, SkillRegistry
from agent_skills.tools import create_skill_tools


class TestSkillTools:
    def _get_tool_funcs(self, registry: SkillRegistry) -> dict:
        """Helper to get the underlying tool functions by name."""
        tools = create_skill_tools(registry)
        return {t.tool_name: t._tool_func for t in tools}

    def test_creates_three_tools(self):
        reg = FileSystemSkillRegistry()
        tools = create_skill_tools(reg)
        assert len(tools) == 3
        names = {t.tool_name for t in tools}
        assert names == {"list_skills", "activate_skill", "read_skill_resource"}

    def test_list_skills_empty(self):
        reg = FileSystemSkillRegistry()
        funcs = self._get_tool_funcs(reg)
        result = funcs["list_skills"]()
        assert "No skills" in result

    def test_list_skills_with_skills(self, minimal_skill: Path):
        reg = FileSystemSkillRegistry()
        reg.load_skill(minimal_skill)
        funcs = self._get_tool_funcs(reg)
        result = funcs["list_skills"]()
        assert "my-skill" in result
        assert "test skill" in result

    def test_activate_skill_success(self, minimal_skill: Path):
        reg = FileSystemSkillRegistry()
        reg.load_skill(minimal_skill)
        funcs = self._get_tool_funcs(reg)
        result = funcs["activate_skill"](skill_name="my-skill")
        assert "Do the thing step by step." in result

    def test_activate_skill_with_resources(self, full_skill: Path):
        reg = FileSystemSkillRegistry()
        reg.load_skill(full_skill)
        funcs = self._get_tool_funcs(reg)
        result = funcs["activate_skill"](skill_name="full-skill")
        assert "Available resources:" in result
        assert "run.sh" in result

    def test_activate_missing_skill(self):
        reg = FileSystemSkillRegistry()
        funcs = self._get_tool_funcs(reg)
        result = funcs["activate_skill"](skill_name="nope")
        assert "Error" in result

    def test_read_resource_success(self, full_skill: Path):
        reg = FileSystemSkillRegistry()
        reg.load_skill(full_skill)
        funcs = self._get_tool_funcs(reg)
        result = funcs["read_skill_resource"](
            skill_name="full-skill",
            resource_type="scripts",
            file_path="run.sh",
        )
        assert "echo hello" in result

    def test_read_resource_error(self):
        reg = FileSystemSkillRegistry()
        funcs = self._get_tool_funcs(reg)
        result = funcs["read_skill_resource"](
            skill_name="nope",
            resource_type="scripts",
            file_path="run.sh",
        )
        assert "Error" in result
