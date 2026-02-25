"""Tests for data models."""

import pytest
from pydantic import ValidationError

from agent_skills.models import SkillMetadata


class TestSkillMetadata:
    def test_valid_name(self):
        m = SkillMetadata(name="pdf-processing", description="Process PDFs.")
        assert m.name == "pdf-processing"

    def test_single_char_name(self):
        m = SkillMetadata(name="a", description="A skill.")
        assert m.name == "a"

    def test_name_uppercase_rejected(self):
        with pytest.raises(ValidationError, match="lowercase"):
            SkillMetadata(name="PDF-Processing", description="Bad name.")

    def test_name_leading_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="hyphen"):
            SkillMetadata(name="-pdf", description="Bad name.")

    def test_name_trailing_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="hyphen"):
            SkillMetadata(name="pdf-", description="Bad name.")

    def test_name_consecutive_hyphens_rejected(self):
        with pytest.raises(ValidationError, match="consecutive"):
            SkillMetadata(name="pdf--processing", description="Bad name.")

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            SkillMetadata(name="a" * 65, description="Too long name.")

    def test_name_empty_rejected(self):
        with pytest.raises(ValidationError):
            SkillMetadata(name="", description="Empty name.")

    def test_description_too_long_rejected(self):
        with pytest.raises(ValidationError):
            SkillMetadata(name="ok", description="x" * 1025)

    def test_description_empty_rejected(self):
        with pytest.raises(ValidationError):
            SkillMetadata(name="ok", description="")

    def test_optional_fields_default_none(self):
        m = SkillMetadata(name="test", description="Test.")
        assert m.license is None
        assert m.compatibility is None
        assert m.metadata is None
        assert m.allowed_tools is None

    def test_all_optional_fields(self):
        m = SkillMetadata(
            name="test",
            description="Test.",
            license="MIT",
            compatibility="Requires docker",
            metadata={"author": "me"},
            allowed_tools=["Read", "Bash(git:*)"],
        )
        assert m.license == "MIT"
        assert m.compatibility == "Requires docker"
        assert m.metadata == {"author": "me"}
        assert m.allowed_tools == ["Read", "Bash(git:*)"]

    def test_compatibility_too_long_rejected(self):
        with pytest.raises(ValidationError):
            SkillMetadata(name="ok", description="Test.", compatibility="x" * 501)
