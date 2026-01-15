# Managing Instructions

Instructions are rules and guidelines that AI assistants must follow. Agent Scaffold allows you to manage these instructions centrally and apply them either globally or to specific file paths.

## Types of Instructions

1. **Repo-Scope (Global)**: These apply to the entire repository. Examples: "Always use English", "Follow the Code of Conduct".
2. **Path-Scope**: These apply only to files matching a glob pattern. Examples: "Use TypeScript for .ts files", "Use Pytest for tests/".

## Adding an Instruction

Use the `add-instruction` command.

### Global Instruction

```bash
agent-scaffold add-instruction general-rules --scope repo
```

### Path-Scoped Instruction

```bash
agent-scaffold add-instruction python-style --scope path --apply-to "**/*.py"
```

## Editing Instructions

Edit the generated Markdown files in `.agents/instructions/`.

**Example `.agents/instructions/python-style.md`:**

```markdown
# Python Style Guide

- Follow PEP 8.
- Use type hints for all function arguments.
- Docstrings must use the Google style.
```

## How Targets Consume Instructions

### GitHub Copilot
- **Repo-Scope**: All repo-scoped instructions are compiled into a single file `.github/copilot-instructions.md`. Copilot automatically reads this file.
- **Path-Scope**: Separate files are generated in `.github/instructions/`. For example, `.github/instructions/python-style.instructions.md`. These files include a YAML frontmatter `applyTo: "**/*.py"` which Copilot uses to contextually apply the rules when you are editing a matching file.

### OpenCode
- All instructions are indexed in `AGENTS.md` (or your configured rules file).
- The `opencode.json` configuration lists these rules with their glob patterns, allowing OpenCode to respect the same scopes.
