"""Demo: loading skills and creating a Strands agent with skill tools."""

from pathlib import Path

from spec_agent_skills import SkillRegistry


def main():
    skills_dir = Path(__file__).parent / "skills"

    registry = SkillRegistry()

    if skills_dir.is_dir():
        loaded = registry.load_skills_from_directory(skills_dir)
        print(f"Loaded {len(loaded)} skill(s): {registry.skill_names}")
    else:
        print(f"No skills directory found at {skills_dir}")
        return

    # Generate system prompt with skill metadata
    system_prompt = registry.to_system_prompt()
    print("\n--- System Prompt ---")
    print(system_prompt)

    # Get Strands tools for use with an Agent
    tools = registry.get_tools()
    print(f"\n--- Tools ({len(tools)}) ---")
    for t in tools:
        print(f"  - {t.tool_name}")

    # Example: create an agent (requires model credentials)
    # from strands import Agent
    # agent = Agent(tools=tools, system_prompt=system_prompt)
    # agent("List the available skills and activate the most relevant one.")


if __name__ == "__main__":
    main()
