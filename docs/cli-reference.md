# CLI Reference

This reference documents the available commands in the `agent-scaffold` CLI.

Global Options:
- `--root <path>`: Specify the project root directory (default: current directory).
- `--version`: Show the version.
- `--help`: Show help message.

## `init`

Initialize a new `.agents/` directory structure and manifest.

```bash
agent-scaffold init [OPTIONS]
```

**Options:**
- `--name, -n <name>`: Project name (defaults to directory name).
- `--force, -f`: Overwrite existing manifest if it exists.

## `add-agent`

Add a new agent artifact.

```bash
agent-scaffold add-agent [OPTIONS] ARTIFACT_ID
```

**Arguments:**
- `ARTIFACT_ID`: Unique kebab-case identifier (e.g., `code-reviewer`).

**Options:**
- `--description, -d <text>`: Brief description of the agent.
- `--opencode-only`: Enable this agent only for OpenCode.
- `--copilot-only`: Enable this agent only for Copilot targets.

## `add-prompt`

Add a new prompt artifact (primarily for Copilot).

```bash
agent-scaffold add-prompt [OPTIONS] ARTIFACT_ID
```

**Arguments:**
- `ARTIFACT_ID`: Unique kebab-case identifier (e.g., `explain-code`).

**Options:**
- `--title, -t <text>`: Human-readable title.
- `--description, -d <text>`: Brief description.
- `--agent, -a <name>`: Default agent to use (e.g., `ask`, `workspace`).

## `add-instruction`

Add a new instruction artifact.

```bash
agent-scaffold add-instruction [OPTIONS] ARTIFACT_ID
```

**Arguments:**
- `ARTIFACT_ID`: Unique kebab-case identifier (e.g., `typescript-rules`).

**Options:**
- `--scope, -s <repo|path>`: **Required**. Scope of the instruction.
  - `repo`: Applies globally to the repository.
  - `path`: Applies to specific file paths.
- `--apply-to, -a <glob>`: Glob pattern for path-scoped instructions (required if scope is `path`). E.g., `**/*.ts`.

## `add-skill`

Add a new skill artifact.

```bash
agent-scaffold add-skill [OPTIONS] ARTIFACT_ID
```

**Arguments:**
- `ARTIFACT_ID`: Unique kebab-case identifier (e.g., `api-client`).

**Options:**
- `--name, -n <text>`: Display name for the skill.
- `--description, -d <text>`: Description of the skill.

## `sync`

Generate target files from the manifest.

```bash
agent-scaffold sync [OPTIONS]
```

**Options:**
- `--prune`: Remove generated files that are no longer present in the manifest.
- `--dry-run`: Show what would be generated without writing to disk.
- `--target, -t <name>`: Only sync a specific target (e.g., `opencode`).

## `doctor`

Validate manifest and check file integrity.

```bash
agent-scaffold doctor
```

Checks performed:
- Manifest existence and validity.
- Existence of canonical files referenced in manifest.
- Artifact ID uniqueness and naming conventions.
- Instruction configurations.
