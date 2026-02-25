from pathlib import Path
from typing import Optional

from agent_skills import SkillRegistry, render_system_prompt

from personas.models import Persona, PersonaRecords


class PersonaRepository:
    def __init__(self, skill_registry: SkillRegistry, data_dir: str = "data"):
        self.skill_registry = skill_registry
        self.data_dir = Path(data_dir)
        self._load_records()

    def _load_records(self):
        with open(self.data_dir / "personas.json", "r") as json_file:
            json_data = json_file.read()
            self.records = PersonaRecords.model_validate_json(json_data)

    def get_persona(self, name: str) -> Optional[Persona]:
        if (record := self.records.root.get(name)) is None:
            return None

        skills = []
        for skill_name in record.skill_names:
            skill = self.skill_registry.get_skill(skill_name)
            if not skill:
                raise ValueError(f"No skill named '{skill_name} found.")
            skills.append(skill)

        skill_metadata = [s.metadata for s in skills]
        sys_prompt = render_system_prompt(record.sys_prompt, skill_metadata)
        return Persona(name=name, sys_prompt=sys_prompt, skills=skills)
