# agent-scaffold

Multi-agent scaffold for AI coding assistants.

## Overview

`agent-scaffold` is a CLI tool that maintains a single source of truth for AI coding assistant configurations under `.agents/`, generating target-specific files for:

- **OpenCode** - Config-driven via `opencode.json`
- **GitHub Copilot VS Code** - Bridge files under `.github/`
- **GitHub Copilot CLI** - Shares `.github/` with VS Code

## Installation

```bash
# Using uvx from GitHub (recommended)
uvx --from git+https://github.com/yldgio/dotgents agent-scaffold <command>

# Install from GitHub with uv
uv pip install git+https://github.com/yldgio/dotgents

# Install from GitHub with pip
pip install git+https://github.com/yldgio/dotgents

# For a specific version/tag
uvx --from git+https://github.com/yldgio/dotgents@v0.1.0 agent-scaffold <command>
```

### Shell Alias (Optional)

For convenience, add an alias to your shell configuration:

```bash
# ~/.bashrc or ~/.zshrc
alias agent-scaffold='uvx --from git+https://github.com/yldgio/dotgents agent-scaffold'

# Then use simply:
agent-scaffold init
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

### CI/CD

This project uses GitHub Actions for continuous integration:

- **Test workflow** (`.github/workflows/test.yml`): Runs on every push and PR
  - Linting with ruff
  - Type checking with mypy
  - Tests on Python 3.10, 3.11, 3.12

- **Release workflow** (`.github/workflows/release.yml`): Runs on version tags
  - Builds the package
  - Creates GitHub release with artifacts

### Creating a Release

To create a new release:

```bash
# Update version in pyproject.toml and src/agent_scaffold/__init__.py
# Then tag and push:
git tag v0.1.0
git push origin v0.1.0
```

Users can then install a specific version:

```bash
uvx --from git+https://github.com/yldgio/dotgents@v0.1.0 agent-scaffold init
```

## License

MIT
