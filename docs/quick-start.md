# Quick Start Guide

This guide will walk you through setting up Agent Scaffold in a new or existing project, creating your first agent, and syncing configuration files.

## 1. Initialize the Project

Navigate to your project root and run the initialization command.

```bash
agent-scaffold init
```

This creates the `.agents/` directory structure and a `manifest.yaml` configuration file.

```text
.agents/
├── agents/          # Agent definitions
├── commands/        # Command templates (future use)
├── instructions/    # Rule files
├── prompts/         # Copilot prompts
├── skills/          # Skill bundles
└── manifest.yaml    # Main config
```

It also creates a sample instruction file `repo-default.md`.

## 2. Add an Instruction

Let's add a coding standard instruction for TypeScript files.

```bash
agent-scaffold add-instruction typescript --scope path --apply-to "**/*.ts"
```

This creates `.agents/instructions/typescript.md`. Edit this file to add your specific rules:

```markdown
# TypeScript Guidelines

- Use strict mode.
- Prefer interfaces over types.
- No `any`.
```

## 3. Add an Agent

Create a specialist agent for code reviews.

```bash
agent-scaffold add-agent reviewer --description "Code review specialist"
```

This creates `.agents/agents/reviewer.md`. Opens this file to define the agent's system prompt and capabilities.

## 4. Add a Prompt (for Copilot VS Code)

Create a custom prompt to explain complex logic.

```bash
agent-scaffold add-prompt explain-complex --title "Explain Complex Logic"
```

## 5. Sync Configuration

Now, generate the target-specific configuration files for OpenCode and Copilot.

```bash
agent-scaffold sync
```

You will see output indicating which files were created:
- `opencode.json` (for OpenCode)
- `.github/agents/reviewer.agent.md`
- `.github/prompts/explain-complex.prompt.md`
- `.github/instructions/...`

## 6. Verify Setup

Run the doctor command to ensure everything is correctly configured.

```bash
agent-scaffold doctor
```

If all checks pass, your project is ready! Your AI assistants will now pick up the new configurations.

## Next Steps

- Explore the [CLI Reference](cli-reference.md) for more commands.
- Learn about the [Project Structure](project-structure.md).
