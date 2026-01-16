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
agent-scaffold add-command test --description "Run test suite"

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
│   ├── commands/           # OpenCode slash commands
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
| `add-command <id>` | Add a new OpenCode slash command |
| `sync` | Generate target files |
| `doctor` | Validate configuration |

## Key Principles

1. **Single source of truth** - All content lives in `.agents/`
2. **No content duplication** - Generated files contain pointers, not copies
3. **Idempotent sync** - Running sync repeatedly produces identical output
4. **Config-driven** - Central manifest drives all generation

## Documentation

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed implementation guide.

## Development

### Setup

```bash
# Clone and install in development mode
git clone https://github.com/yldgio/dotgents.git
cd dotgents
uv venv
uv pip install -e ".[dev]"
```

### Code Quality

This project uses `ruff` for linting/formatting and `mypy` for type checking:

```bash
# Run linter
ruff check src/ tests/

# Auto-fix linting issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/

# Check formatting (CI mode)
ruff format --check src/ tests/

# Type checking
mypy src/
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/agent_scaffold
```

### All Checks

Run all quality checks before committing:

```bash
ruff check src/ tests/ && ruff format --check src/ tests/ && mypy src/ && pytest tests/
```

## License

MIT
