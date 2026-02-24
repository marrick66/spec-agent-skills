"""Validation logic for the Agent Skills specification."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Skill


def validate_skill_directory(skill_dir: Path) -> None:
    """Validate that a path is a valid skill directory.

    Raises:
        FileNotFoundError: If directory or SKILL.md doesn't exist.
        ValueError: If path is not a directory.
    """
    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
    if not skill_dir.is_dir():
        raise ValueError(f"Path is not a directory: {skill_dir}")
    if not (skill_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"SKILL.md not found in: {skill_dir}")


def validate_name_matches_directory(name: str, dir_name: str) -> None:
    """Validate that the skill name matches its directory name.

    Raises:
        ValueError: If name does not match directory name.
    """
    if name != dir_name:
        raise ValueError(
            f"Skill name '{name}' must match directory name '{dir_name}'"
        )


def validate_resource_path(
    skill: Skill, resource_type: str, file_path: str
) -> Path:
    """Validate and resolve a resource file path, preventing path traversal.

    Args:
        skill: The skill containing the resource.
        resource_type: One of 'scripts', 'references', 'assets'.
        file_path: Relative path within the resource directory.

    Returns:
        Resolved absolute Path to the resource file.

    Raises:
        ValueError: If resource_type is invalid or path traversal is detected.
        FileNotFoundError: If the resource directory or file doesn't exist.
    """
    dir_map = {
        "scripts": skill.resources.scripts_dir,
        "references": skill.resources.references_dir,
        "assets": skill.resources.assets_dir,
    }

    if resource_type not in dir_map:
        raise ValueError(
            f"Invalid resource type: {resource_type}. "
            f"Must be one of: {list(dir_map.keys())}"
        )

    base_dir = dir_map[resource_type]
    if base_dir is None:
        raise FileNotFoundError(
            f"Skill '{skill.metadata.name}' has no {resource_type}/ directory"
        )

    resolved = (base_dir / file_path).resolve()

    if not str(resolved).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal detected: {file_path}")

    if not resolved.is_file():
        raise FileNotFoundError(f"Resource file not found: {file_path}")

    return resolved
