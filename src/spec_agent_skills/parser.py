"""SKILL.md parsing — frontmatter, body, and directory discovery."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Skill, SkillMetadata, SkillResources
from .validation import validate_name_matches_directory, validate_skill_directory


def parse_skill(skill_path: str | Path) -> Skill:
    """Parse a skill directory into a Skill model.

    Args:
        skill_path: Path to the skill directory containing SKILL.md.

    Returns:
        A fully populated Skill instance.

    Raises:
        FileNotFoundError: If SKILL.md does not exist.
        ValueError: If frontmatter is invalid or missing required fields.
    """
    skill_dir = Path(skill_path).resolve()
    validate_skill_directory(skill_dir)

    skill_md = skill_dir / "SKILL.md"
    raw = skill_md.read_text(encoding="utf-8")

    frontmatter, body = _split_frontmatter(raw)

    # Transform allowed-tools from space-delimited string to list
    if "allowed-tools" in frontmatter:
        value = frontmatter.pop("allowed-tools")
        if isinstance(value, str):
            frontmatter["allowed_tools"] = value.split()
        elif isinstance(value, list):
            frontmatter["allowed_tools"] = value

    metadata = SkillMetadata(**frontmatter)
    validate_name_matches_directory(metadata.name, skill_dir.name)

    resources = _discover_resources(skill_dir)

    return Skill(
        metadata=metadata,
        instructions=body,
        resources=resources,
        path=skill_dir,
        activated=False,
    )


def _split_frontmatter(content: str) -> tuple[dict, str]:
    """Split SKILL.md content into YAML frontmatter dict and markdown body.

    Expects the file to begin with '---', followed by YAML,
    followed by '---', followed by the markdown body.
    """
    if not content.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter delimited by ---")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter must be delimited by --- on both sides")

    frontmatter = yaml.safe_load(parts[1])
    if not isinstance(frontmatter, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping")

    body = parts[2].strip()
    return frontmatter, body


def _discover_resources(skill_dir: Path) -> SkillResources:
    """Check for optional subdirectories."""
    return SkillResources(
        scripts_dir=skill_dir / "scripts" if (skill_dir / "scripts").is_dir() else None,
        references_dir=(
            skill_dir / "references"
            if (skill_dir / "references").is_dir()
            else None
        ),
        assets_dir=skill_dir / "assets" if (skill_dir / "assets").is_dir() else None,
    )
