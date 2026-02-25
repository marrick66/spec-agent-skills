# agent-skills

A Python library that implements the [Agent Skills specification](https://agentskills.io/specification) as [Strands Agents](https://github.com/strands-agents/sdk-python) tools.

Load skills from disk, register them in memory, and give your agent tools for progressive discovery and activation — all following the open Agent Skills format.

## Installation

```bash
pip install agent-skills
```

## Quick Start

```python
from strands import Agent
from agent_skills import SkillRegistry

registry = SkillRegistry()
registry.load_skills_from_directory("./skills")

agent = Agent(
    tools=registry.get_tools(),
    system_prompt=registry.to_system_prompt(),
)

agent("List the available skills and activate the most relevant one.")
```

## License

See [LICENSE](../../LICENSE) for details.
