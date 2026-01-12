# agent-scaffold

Multi-agent scaffold for AI coding assistants.

## Overview

`agent-scaffold` is a CLI tool that maintains a single source of truth for AI coding assistant configurations under `.agents/`, generating target-specific files for:

- **OpenCode** - Config-driven via `opencode.json`
- **GitHub Copilot VS Code** - Bridge files under `.github/`
- **GitHub Copilot CLI** - Shares `.github/` with VS Code

## Installation

```bash
# Using uvx (recommended)
uvx agent-scaffold <command>

# Or install with uv
uv pip install agent-scaffold

# Or install with pip
pip install agent-scaffold
```

## Quick Start

```bash
# Initialize a new project
agent-scaffold init

# Add artifacts
agent-scaffold add-agent reviewer --description "Code review specialist"
agent-scaffold add-prompt explain-code --title "Explain Code"
agent-scaffold add-instruction typescript --scope path --apply-to "**/*.ts"

# Generate target files
agent-scaffold sync

# Validate configuration
agent-scaffold doctor
```

## Project Structure

After initialization, your project will have:

```
your-project/
├── .agents/
│   ├── manifest.yaml       # Central configuration
│   ├── prompts/            # Prompt templates
│   ├── agents/             # Agent definitions
│   ├── instructions/       # Instruction files
│   └── skills/             # Skill bundles
├── .github/                # Generated Copilot files
│   ├── prompts/
│   ├── agents/
│   ├── instructions/
│   └── copilot-instructions.md
├── opencode.json           # Generated OpenCode config
└── AGENTS.md               # Generated rules index
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize .agents/ structure |
| `add-prompt <id>` | Add a new prompt |
| `add-agent <id>` | Add a new agent |
| `add-instruction <id>` | Add a new instruction |
| `add-skill <id>` | Add a new skill |
| `sync` | Generate target files |
| `doctor` | Validate configuration |

## Key Principles

1. **Single source of truth** - All content lives in `.agents/`
2. **No content duplication** - Generated files contain pointers, not copies
3. **Idempotent sync** - Running sync repeatedly produces identical output
4. **Config-driven** - Central manifest drives all generation

## Documentation

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed implementation guide.

## License

MIT
