# spec-agent-skills

A Python library that implements the [Agent Skills specification](https://agentskills.io/specification) as [Strands Agents](https://github.com/strands-agents/sdk-python) tools.

Load skills from disk, register them in memory, and give your agent tools for progressive discovery and activation — all following the open Agent Skills format.

## Installation

```bash
pip install spec-agent-skills
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add spec-agent-skills
```

## Quick Start

```python
from strands import Agent
from spec_agent_skills import SkillRegistry

# Load skills from a directory
registry = SkillRegistry()
registry.load_skills_from_directory("./skills")

# Create an agent with skill tools and system prompt
agent = Agent(
    tools=registry.get_tools(),
    system_prompt=registry.to_system_prompt(),
)

agent("List the available skills and activate the most relevant one.")
```

## How It Works

The library follows the spec's **progressive disclosure** model to keep context usage efficient:

| Level | Tool | Context Cost | What's Loaded |
|-------|------|-------------|---------------|
| 1. Metadata | `list_skills()` | ~100 tokens/skill | Name + description only |
| 2. Instructions | `activate_skill(name)` | < 5000 tokens | Full SKILL.md body + resource listing |
| 3. Resources | `read_skill_resource(name, type, path)` | As needed | Individual files from scripts/, references/, assets/ |

The agent discovers skills via metadata in the system prompt, activates the ones it needs, and loads specific resources on demand.

## API Reference

### SkillRegistry

The central class for managing skills.

```python
from spec_agent_skills import SkillRegistry

registry = SkillRegistry()
```

#### Loading Skills

```python
# Load a single skill from a directory path
registry.load_skill("./skills/my-skill")

# Load all skills from subdirectories of a parent path
registry.load_skills_from_directory("./skills")
```

#### System Prompt Generation

```python
# Generate <available_skills> XML block for the agent's system prompt
system_prompt = registry.to_system_prompt()
```

Produces XML in the format recommended by the spec:

```xml
<available_skills>
  <skill>
    <name>my-skill</name>
    <description>What this skill does and when to use it.</description>
  </skill>
</available_skills>
```

#### Agent Tools

```python
# Get Strands @tool functions bound to this registry
tools = registry.get_tools()
# Returns: [list_skills, activate_skill, read_skill_resource]
```

#### Other Methods

```python
registry.get_skill("name")       # Get a Skill by name (or None)
registry.list_skills()            # List all SkillMetadata
registry.activate_skill("name")   # Mark active and return instructions
registry.read_resource("name", "scripts", "run.sh")  # Read a resource file
registry.skill_names              # List of loaded skill names
len(registry)                     # Number of loaded skills
"name" in registry                # Check if a skill is loaded
```

### Data Models

```python
from spec_agent_skills import Skill, SkillMetadata, SkillResources
```

- **`SkillMetadata`** — Frontmatter fields: `name`, `description`, plus optional `license`, `compatibility`, `metadata`, `allowed_tools`
- **`SkillResources`** — Tracks optional directories (`scripts_dir`, `references_dir`, `assets_dir`) with a `list_files(resource_type)` method
- **`Skill`** — Full representation: `metadata`, `instructions`, `resources`, `path`, `activated`

### Standalone Parsing

```python
from spec_agent_skills import parse_skill, validate_skill_directory

validate_skill_directory(Path("./skills/my-skill"))  # Raises on invalid
skill = parse_skill("./skills/my-skill")             # Returns a Skill
```

## Skill Format

A skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```
my-skill/
├── SKILL.md            # Required
├── scripts/            # Optional — executable code
├── references/         # Optional — additional documentation
└── assets/             # Optional — templates, data files, images
```

### SKILL.md

```yaml
---
name: my-skill
description: What this skill does and when to use it.
license: Apache-2.0                       # optional
compatibility: Requires Python 3.13+      # optional
metadata:                                  # optional
  author: my-org
  version: "1.0"
allowed-tools: Bash(git:*) Read           # optional
---

# Instructions

Step-by-step instructions for the agent go here.
```

See the full [Agent Skills specification](https://agentskills.io/specification) for details.

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v
```

## License

See [LICENSE](LICENSE) for details.
