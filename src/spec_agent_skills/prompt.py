"""Generate <available_skills> XML block for agent system prompts."""

from __future__ import annotations

from xml.sax.saxutils import escape

from .models import SkillMetadata


def render_system_prompt(skills: list[SkillMetadata]) -> str:
    """Render the <available_skills> XML block for system prompts.

    Follows the Agent Skills specification format. Only includes
    name and description (metadata level) per the progressive disclosure model.

    Args:
        skills: List of SkillMetadata instances to include.

    Returns:
        XML string suitable for inclusion in a system prompt.
        Returns empty string if no skills are provided.
    """
    if not skills:
        return ""

    lines = ["<available_skills>"]
    for s in skills:
        lines.append("  <skill>")
        lines.append(f"    <name>{escape(s.name)}</name>")
        lines.append(f"    <description>{escape(s.description)}</description>")
        lines.append("  </skill>")
    lines.append("</available_skills>")

    return "\n".join(lines)
