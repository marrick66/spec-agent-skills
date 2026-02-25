"""Data models for the Agent Skills specification."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class SkillMetadata(BaseModel):
    """Lightweight metadata loaded at startup (~100 tokens per skill).

    Corresponds to the YAML frontmatter of a SKILL.md file.
    """

    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1, max_length=1024)
    license: str | None = Field(default=None)
    compatibility: str | None = Field(default=None, max_length=500)
    metadata: dict[str, str] | None = Field(default=None)
    allowed_tools: list[str] | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        pattern = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
        if not re.match(pattern, v):
            raise ValueError(
                f"Name '{v}' must be lowercase alphanumeric with hyphens, "
                "must not start or end with a hyphen"
            )
        if "--" in v:
            raise ValueError(f"Name '{v}' must not contain consecutive hyphens")
        return v


class SkillResources(BaseModel):
    """Tracks which optional resource directories exist for a skill."""

    scripts_dir: Path | None = None
    references_dir: Path | None = None
    assets_dir: Path | None = None

    model_config = {"arbitrary_types_allowed": True}

    def list_files(self, resource_type: str) -> list[str]:
        """List available files in a resource directory.

        Args:
            resource_type: One of 'scripts', 'references', 'assets'.

        Returns:
            List of relative file paths within the resource directory.
        """
        dir_map = {
            "scripts": self.scripts_dir,
            "references": self.references_dir,
            "assets": self.assets_dir,
        }
        target = dir_map.get(resource_type)
        if target is None or not target.exists():
            return []
        return sorted(
            str(p.relative_to(target)) for p in target.rglob("*") if p.is_file()
        )


class Skill(BaseModel):
    """Complete skill representation with progressive disclosure support.

    The instructions field contains the full SKILL.md body but is only
    exposed to agents when the skill is activated.
    """

    metadata: SkillMetadata
    instructions: str = ""
    resources: SkillResources
    path: Path
    activated: bool = False

    model_config = {"arbitrary_types_allowed": True}
