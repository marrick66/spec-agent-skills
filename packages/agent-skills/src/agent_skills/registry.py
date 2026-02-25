"""Skill registry abstract base class and local filesystem implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import Skill, SkillMetadata
from .parser import parse_skill
from .prompt import render_system_prompt
from .tools import create_skill_tools
from .validation import validate_resource_path


class SkillRegistry(ABC):
    """Abstract base class defining the skill registry interface.

    Concrete implementations must provide skill storage, retrieval,
    activation, and resource access. Convenience methods for system
    prompt generation and tool creation are provided.
    """

    @abstractmethod
    def get_skill(self, name: str) -> Skill | None:
        """Get a loaded skill by name."""

    @abstractmethod
    def list_skills(self) -> list[SkillMetadata]:
        """Return metadata for all loaded skills."""

    @abstractmethod
    def activate_skill(self, name: str) -> str:
        """Mark a skill as activated and return its full instructions.

        Raises:
            KeyError: If no skill with that name is loaded.
        """

    @abstractmethod
    def read_resource(self, skill_name: str, resource_type: str, file_path: str) -> str:
        """Read a resource file from a skill.

        Raises:
            KeyError: If skill not found.
            ValueError: If resource_type is invalid or path traversal detected.
            FileNotFoundError: If resource directory or file doesn't exist.
        """

    @property
    @abstractmethod
    def skill_names(self) -> list[str]:
        """Return names of all loaded skills."""

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __contains__(self, name: str) -> bool: ...

    def to_system_prompt(self, custom_sys_prompt: str) -> str:
        """Generate the system prompt XML block for all loaded skills."""
        return render_system_prompt(custom_sys_prompt, self.list_skills())

    def get_tools(self) -> list:
        """Create and return Strands agent tools bound to this registry."""
        return create_skill_tools(self)


class FileSystemSkillRegistry(SkillRegistry):
    """Filesystem-backed skill repository.

    Loads skills from local directories containing SKILL.md files
    and stores them in memory.

    Usage::

        repo = LocalSkillRepository()
        repo.load_skill("/path/to/my-skill")
        repo.load_skills_from_directory("/path/to/skills/")

        system_prompt = repo.to_system_prompt()
        tools = repo.get_tools()

        agent = Agent(tools=tools, system_prompt=system_prompt)
    """

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def load_skill(self, path: str | Path) -> Skill:
        """Load a single skill from a directory path.

        Args:
            path: Path to a skill directory containing SKILL.md.

        Returns:
            The loaded Skill instance.

        Raises:
            FileNotFoundError: If the path or SKILL.md doesn't exist.
            ValueError: If the skill is invalid or already loaded.
        """
        skill = parse_skill(path)
        if skill.metadata.name in self._skills:
            raise ValueError(f"Skill '{skill.metadata.name}' is already loaded")
        self._skills[skill.metadata.name] = skill
        return skill

    def load_skills_from_directory(self, path: str | Path) -> list[Skill]:
        """Load all skills from subdirectories of the given path.

        Each immediate subdirectory containing a SKILL.md is treated as a skill.

        Args:
            path: Parent directory containing skill subdirectories.

        Returns:
            List of successfully loaded Skill instances.
        """
        parent = Path(path).resolve()
        loaded = []
        for child in sorted(parent.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                loaded.append(self.load_skill(child))
        return loaded

    def get_skill(self, name: str) -> Skill | None:
        """Get a loaded skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> list[SkillMetadata]:
        """Return metadata for all loaded skills."""
        return [s.metadata for s in self._skills.values()]

    def activate_skill(self, name: str) -> str:
        """Mark a skill as activated and return its full instructions.

        Args:
            name: The skill name to activate.

        Returns:
            The markdown body (instructions) from SKILL.md.

        Raises:
            KeyError: If no skill with that name is loaded.
        """
        skill = self._skills.get(name)
        if skill is None:
            raise KeyError(f"Skill '{name}' not found in registry")
        skill.activated = True
        return skill.instructions

    def read_resource(self, skill_name: str, resource_type: str, file_path: str) -> str:
        """Read a resource file from a skill.

        Args:
            skill_name: Name of the skill.
            resource_type: One of 'scripts', 'references', 'assets'.
            file_path: Relative path within the resource directory.

        Returns:
            The file contents as a string.

        Raises:
            KeyError: If skill not found.
            ValueError: If resource_type is invalid or path traversal detected.
            FileNotFoundError: If resource directory or file doesn't exist.
        """
        skill = self._skills.get(skill_name)
        if skill is None:
            raise KeyError(f"Skill '{skill_name}' not found in registry")

        resolved_path = validate_resource_path(skill, resource_type, file_path)
        return resolved_path.read_text(encoding="utf-8")

    @property
    def skill_names(self) -> list[str]:
        """Return names of all loaded skills."""
        return list(self._skills.keys())

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        return name in self._skills
