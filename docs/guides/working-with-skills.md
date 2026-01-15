# Working with Skills

Skills are reusable bundles of functionality—scripts, tools, or knowledge—that agents can leverage.

## Structure of a Skill

A skill in Agent Scaffold is a directory containing at least one file: `SKILL.md`.

```text
.agents/skills/
└── weather-api/
    ├── SKILL.md
    └── fetch_weather.py
```

- **SKILL.md**: A description of the skill and how to use it.
- **Other files**: Scripts or data files that implement the skill.

## Creating a Skill

```bash
agent-scaffold add-skill weather-api --description "Fetches weather data"
```

This creates the directory and the `SKILL.md` file.

## Defining the Skill

Edit `.agents/skills/weather-api/SKILL.md`.

```markdown
# Weather API Skill

This skill allows agents to check the current weather.

## Tools
- `fetch_weather.py`: A Python script that takes a city name as an argument.

## Usage
Run the script using `python .agents/skills/weather-api/fetch_weather.py <city>`.
```

## Discovery

When you run `agent-scaffold sync`:

1.  **Copilot**: The skill directory is mirrored to `.github/skills/`. Copilot agents can then "see" this skill and use its tools if instructed.
2.  **OpenCode**: (Future support planned for explicit tool registration). Currently, the skill serves as documentation for the model.
