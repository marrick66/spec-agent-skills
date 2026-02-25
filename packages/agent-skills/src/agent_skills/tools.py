"""Strands agent tool factory for progressive skill disclosure."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strands import tool

if TYPE_CHECKING:
    from .registry import SkillRegistry


def create_skill_tools(registry: SkillRegistry) -> list:
    """Create Strands agent tools bound to the given registry.

    Returns three tools implementing progressive disclosure:
    1. list_skills — metadata only (~100 tokens each)
    2. activate_skill — full instructions (<5000 tokens)
    3. read_skill_resource — individual resource files (as needed)
    """

    @tool
    def list_skills() -> str:
        """List all available agent skills with their names and descriptions.

        Call this tool to discover which skills are available before activating one.
        Returns skill names and descriptions only (metadata level).

        Returns:
            A formatted list of available skills with name and description.
        """
        skills = registry.list_skills()
        if not skills:
            return "No skills are currently loaded."

        lines = []
        for s in skills:
            lines.append(f"- **{s.name}**: {s.description}")
        return "\n".join(lines)

    @tool
    def activate_skill(skill_name: str) -> str:
        """Activate a skill and load its full instructions.

        Call this after identifying a relevant skill from list_skills.
        Returns the complete instructions from the skill's SKILL.md body.

        Args:
            skill_name: The name of the skill to activate (e.g. 'pdf-processing').

        Returns:
            The full markdown instructions for the skill, or an error message.
        """
        try:
            instructions = registry.activate_skill(skill_name)

            skill = registry.get_skill(skill_name)
            resource_info = []
            if skill:
                for rtype in ("scripts", "references", "assets"):
                    files = skill.resources.list_files(rtype)
                    if files:
                        resource_info.append(f"{rtype.title()}: {', '.join(files)}")

            result = instructions
            if resource_info:
                result += (
                    "\n\n---\nAvailable resources:\n" + "\n".join(resource_info)
                )

            return result
        except KeyError as e:
            return f"Error: {e}"

    @tool
    def read_skill_resource(
        skill_name: str,
        resource_type: str,
        file_path: str,
    ) -> str:
        """Read a resource file from an activated skill.

        Use this to load scripts, reference docs, or assets from a skill's
        optional directories. The skill must be activated first.

        Args:
            skill_name: Name of the skill (e.g. 'pdf-processing').
            resource_type: Type of resource directory: 'scripts', 'references', or 'assets'.
            file_path: Relative path to the file within the resource directory.

        Returns:
            The contents of the requested file, or an error message.
        """
        try:
            return registry.read_resource(skill_name, resource_type, file_path)
        except (KeyError, ValueError, FileNotFoundError) as e:
            return f"Error: {e}"

    return [list_skills, activate_skill, read_skill_resource]
