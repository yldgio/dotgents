# Project Structure

When using Agent Scaffold, your project structure is organized around the `.agents/` directory, which serves as the canonical source of truth.

## Canonical Directory (`.agents/`)

This directory contains all your source material.

| Path | Description |
|------|-------------|
| `manifest.yaml` | The configuration file defining project settings, active targets, and registered artifacts. |
| `agents/` | **Agent definitions**. Markdown files defining the persona, capabilities, and system prompts of your agents. |
| `instructions/` | **Rules and Guidelines**. Markdown files containing instructions relative to the codebase or specific file paths. |
| `prompts/` | **Prompt templates**. Specifically for GitHub Copilot VS Code `.prompt.md` files. |
| `skills/` | **Skill bundles**. Directories containing a `SKILL.md` and related assets/scripts that agents can use. |
| `commands/` | **Command templates**. (Architecture reserved for future OpenCode slash commands). |

## Generated Artifacts

Depending on which targets are enabled in your `manifest.yaml`, the following files and directories are generated. **These files should generally not be edited manually** as they will be overwritten by `agent-scaffold sync`.

### OpenCode Target

| Path | Description |
|------|-------------|
| `opencode.json` | Configuration file located at the project root. Maps agents and instructions using `{ "file": "..." }` references. |
| `AGENTS.md` | A generated index of available agents and instructions, used by OpenCode as a rules entry point. |

### GitHub Copilot Target (VS Code & CLI)

Generated files are placed in the `.github/` directory to be automatically discovered by Copilot.

| Path | Description |
|------|-------------|
| `.github/prompts/` | Contains `*.prompt.md` files. These are small wrappers pointing to `.agents/prompts/`. |
| `.github/agents/` | Contains `*.agent.md` files. Wrappers pointing to `.agents/agents/`. |
| `.github/instructions/` | Contains `*.instructions.md` files for path-scoped rules. |
| `.github/skills/` | Contains skill definitions (Copilot requires `SKILL.md` inside subdirectories). |
| `.github/copilot-instructions.md`| The repository-wide instruction file. Generated from instructions with `scope: repo`. |
