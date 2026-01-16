# AGENTS.md — Multi-Agent Scaffold

> **Maintainer note:** Update this file whenever a new architectural decision is made or an existing decision changes. This file is the source of truth for project scope, conventions, and design rationale.

---

## Project Scope

**agent-scaffold** is a CLI tool that sets up a repository for multi-agent support across multiple AI coding assistants. It maintains a **single source of truth** for prompts, commands, agents, instructions, and skills under `.agents/`, then generates tool-specific configuration or bridge files so each assistant discovers the content in its native format.

### Supported targets (MVP)

| Target          | Description                                      |
| --------------- | ------------------------------------------------ |
| `opencode`      | OpenCode CLI — config-driven via `opencode.json` |
| `copilot-vscode`| GitHub Copilot in VS Code — bridge files under `.github/` |
| `copilot-cli`   | GitHub Copilot CLI — shares `.github/` with VS Code (no prompt files) |

---

## Key Decisions

### 1. No symlinks, no content copying

- Generated files in target directories do **not** duplicate canonical content.
- Instead, they contain a **pointer line** (e.g., `Follow instructions in '.agents/commands/test.md'`) plus optional Markdown links.
- OpenCode uses **`{file:...}` substitution** in `opencode.json` to reference `.agents/...` directly.

### 2. Config-driven approach

- A central **`.agents/manifest.yaml`** defines all artifacts (prompts, commands, agents, instructions, skills) and per-target overrides.
- The CLI reads the manifest to perform deterministic `add-*` and idempotent `sync` operations.

### 3. Distribution via `uvx`

- Primary execution: `uvx agent-scaffold <command> [options]`
- Rationale: isolated, fast, Windows-friendly, fewer dependency collisions.
- Optional `npx` wrapper may be added later.

### 4. Artifact types

| Type          | Canonical location              | Primary target(s)                |
| ------------- | ------------------------------- | -------------------------------- |
| Prompts       | `.agents/prompts/<id>.md`       | `copilot-vscode` (`.github/prompts/*.prompt.md`) |
| Commands      | `.agents/commands/<id>.md`      | `opencode` (`opencode.json → command.<name>`) |
| Agents        | `.agents/agents/<id>.md`        | `opencode`, `copilot-vscode`, `copilot-cli` |
| Instructions  | `.agents/instructions/<id>.md`  | `copilot-vscode`, `copilot-cli`, `opencode` (via `AGENTS.md` index) |
| Skills        | `.agents/skills/<id>/SKILL.md`  | `copilot-vscode`, `copilot-cli` |

### 5. Target-specific conventions

#### OpenCode

- **Config file:** `opencode.json` at repo root.
- **Commands:** `command.<name>.template: {file: "./.agents/commands/<id>.md"}`.
- **Agents:** `agent.<name>.prompt: {file: "./.agents/agents/<id>.md"}`.
- **Rules:** `instructions` array with globs + generated `AGENTS.md` index.

#### GitHub Copilot (VS Code)

- **Prompt files:** `.github/prompts/<id>.prompt.md` (YAML frontmatter + pointer body).
- **Agents:** `.github/agents/<id>.agent.md`.
- **Instructions:** `.github/copilot-instructions.md` (repo-wide) + `.github/instructions/<id>.instructions.md` (path-scoped with `applyTo`).
- **Skills:** `.github/skills/<id>/SKILL.md`.

#### GitHub Copilot CLI

- Same as VS Code **except prompt files are IDE-only** (not generated for CLI target).

### 6. Idempotent `sync`

- Always regenerates target files from scratch using stable ordering (sorted by `id`).
- Never modifies canonical `.agents/**` content.
- Optional `--prune` flag removes stale generated files.

### 7. Deterministic `add-*` commands

- `add-prompt <id>` → creates canonical file + manifest entry.
- `add-command <id>` → creates canonical file + manifest entry.
- `add-agent <id>` → creates canonical file + manifest entry.
- `add-instruction <id> --scope repo|path [--apply-to <glob>]` → creates canonical file + manifest entry.
- `add-skill <id>` → creates canonical dir + `SKILL.md` + manifest entry.

---

## Open / Future Considerations

1. **Stub reliability:** Copilot may not always "follow" pointer lines automatically; keep inline summaries short but meaningful.
2. **Skills bridge:** Skills are discovered by reading `SKILL.md`; may need to inline minimal content rather than pure pointer.
3. **Root `AGENTS.md`:** This file doubles as the OpenCode rules index; keep it concise and link to `.agents/instructions/...`.
4. **Additional targets:** Claude Code, Gemini CLI, others can be added post-MVP by extending `targets` in the manifest schema.

---

## Updating This File

Whenever you:

- Add or remove a supported target,
- Change the manifest schema,
- Alter generated file conventions,
- Make any architectural or design decision,

**you must update this `AGENTS.md`** to reflect the change. Keep sections concise; link to `.github/prompts/plan-agent-scaffold.prompt.md` for detailed schema documentation.

## Instructions for Updating This File

**When to update AGENTS.md:**

- New agent added or removed
- Architecture changes (new services, patterns)
- New security requirements
- API endpoint changes
- Key file locations change
- New quality/security standards adopted

**How to update:**

1. Keep content concise (this file should be <150 lines)
2. Use tables and code blocks for clarity
3. Update "Last Updated" date
4. Remove outdated information (don't accumulate)
5. Focus on what an LLM needs to assist effectively

**Do NOT include:**

- Implementation details (reference source files instead)
- Verbose explanations (link to PLAN.md for details)
- Historical changes (use git history)
- Sensitive values (keys, passwords)
