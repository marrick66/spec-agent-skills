"""Generate <available_skills> XML block for agent system prompts."""

from __future__ import annotations

from xml.sax.saxutils import escape

from jinja2 import Template

from .models import SkillMetadata

SKILLS_SYSTEM_PROMPT_TEMPLATE = Template("""
{{custom_system_prompt}}

## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

<skills_instructions>
**How to Use Skills:**

Your efforts are greatly aided by reading the skill documentation BEFORE writing any code, creating any files, or using any computer tools.
Skills follow a **progressive disclosure** pattern - you know they exist (name + description above), but you only read the full instructions when needed:

1. **Recognize when a skill applies**: Check if the user's task matches any skill's description
2. **Read the skill's full instructions**: 
   - If a `skill` tool is available, call it with the skill name
     - `skill(skill_name="web-research")` - invoke the web-research skill
   - When a user's request matches one of the available skills, use the use_skill tool
     - `use_skill(skill_name="skill-name", request="specific request")`
   - Alternative: Use the absolute path shown above to read SKILL.md directly
   - Only use skills listed in <available_skills> below
3. **Follow the skill's instructions**: SKILL.md contains step-by-step workflows, best practices, and examples
4. **Access supporting files**: Skills may include Python scripts, configs, or reference docs - always use absolute paths

**When to Use Skills:**
- When the user's request matches a skill's domain (e.g., "research X" → web-research skill)
- When you need specialized knowledge or structured workflows
- When a skill provides proven patterns for complex tasks

**Remember:** Skills are tools to make you more capable and consistent. When in doubt, check if a skill exists for the task!
</skills_instructions>

<available_skills>
{{skills_list}}
</available_skills>
""")


def render_system_prompt(custom_sys_prompt: str, skills: list[SkillMetadata]) -> str:
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

    lines = []
    for s in skills:
        lines.append("  <skill>")
        lines.append(f"    <name>{escape(s.name)}</name>")
        lines.append(f"    <description>{escape(s.description)}</description>")
        lines.append("  </skill>")

    skills_list = "\n".join(lines)

    return SKILLS_SYSTEM_PROMPT_TEMPLATE.render(
        custom_system_prompt=custom_sys_prompt, skills_list=skills_list
    )
