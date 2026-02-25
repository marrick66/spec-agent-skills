"""Tests for system prompt XML generation."""

from agent_skills.models import SkillMetadata
from agent_skills.prompt import render_system_prompt


class TestRenderSystemPrompt:
    def test_empty_list(self):
        assert render_system_prompt("", []) == ""

    def test_single_skill(self):
        skills = [SkillMetadata(name="test", description="A test skill.")]
        result = render_system_prompt("", skills)
        assert "<available_skills>" in result
        assert "</available_skills>" in result
        assert "<name>test</name>" in result
        assert "<description>A test skill.</description>" in result

    def test_multiple_skills(self):
        skills = [
            SkillMetadata(name="skill-a", description="First skill."),
            SkillMetadata(name="skill-b", description="Second skill."),
        ]
        result = render_system_prompt("", skills)
        assert result.count("<skill>") == 2
        assert "skill-a" in result
        assert "skill-b" in result

    def test_xml_escaping(self):
        skills = [
            SkillMetadata(
                name="test",
                description='Handles <special> & "characters".',
            )
        ]
        result = render_system_prompt("", skills)
        assert "&lt;special&gt;" in result
        assert "&amp;" in result
