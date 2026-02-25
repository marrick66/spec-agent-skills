from typing import Any, Dict, List

from agent_skills import Skill
from pydantic import BaseModel, Field, RootModel


class PersonaRecord(BaseModel):
    name: str = Field(..., description="The name of the agent persona.")
    sys_prompt: str = Field(..., description="The system prompt for the persona.")
    skill_names: List[str] = Field(
        ..., description="The list of skills this personal has."
    )


class PersonaRecords(RootModel[Dict[str, PersonaRecord]]):
    pass


class Persona(BaseModel):
    name: str = Field(..., description="The name of the agent persona.")
    sys_prompt: str = Field(..., description="The system prompt for the persona.")
    skills: List[Skill] = Field(
        ..., description="The list of skills this personal has."
    )
    extra_tools: List[Any] = Field(
        default=[], description="Any extra tools outside of what the skills possess."
    )
