"""Shared fixtures for Agent Skills tests."""

from pathlib import Path

import pytest


@pytest.fixture
def minimal_skill(tmp_path: Path) -> Path:
    """Create a minimal valid skill directory."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill for unit testing.\n"
        "---\n"
        "\n"
        "# Instructions\n"
        "\n"
        "Do the thing step by step.\n"
    )
    return skill_dir


@pytest.fixture
def full_skill(tmp_path: Path) -> Path:
    """Create a skill with all optional fields and directories."""
    skill_dir = tmp_path / "full-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: full-skill\n"
        "description: A fully-featured skill with all optional fields.\n"
        "license: Apache-2.0\n"
        "compatibility: Requires Python 3.13+\n"
        'metadata:\n'
        '  author: test-org\n'
        '  version: "1.0"\n'
        "allowed-tools: Bash(git:*) Read\n"
        "---\n"
        "\n"
        "# Full Skill Instructions\n"
        "\n"
        "These are detailed instructions.\n"
    )

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run.sh").write_text("#!/bin/bash\necho hello\n")

    references_dir = skill_dir / "references"
    references_dir.mkdir()
    (references_dir / "REFERENCE.md").write_text("# Reference\n\nDetails here.\n")

    assets_dir = skill_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "template.txt").write_text("Template content.\n")

    return skill_dir


@pytest.fixture
def skills_parent(minimal_skill: Path, full_skill: Path, tmp_path: Path) -> Path:
    """Return tmp_path containing both skill directories."""
    return tmp_path
