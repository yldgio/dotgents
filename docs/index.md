# Agent Scaffold Documentation

Welcome to the documentation for **agent-scaffold**, a CLI tool for managing multi-agent configurations across different AI coding assistants.

## Table of Contents

1. [Introduction](introduction.md)
2. [Installation](installation.md)
3. [Quick Start](quick-start.md)
4. [Project Structure](project-structure.md)
5. [CLI Reference](cli-reference.md)
6. [Manifest Configuration](manifest-configuration.md)
7. [Guides](guides/index.md)
   - [Creating Agents](guides/creating-agents.md)
   - [Managing Instructions](guides/managing-instructions.md)
   - [Working with Skills](guides/working-with-skills.md)

---

## Introduction

**agent-scaffold** provides a "single source of truth" for defining AI agents, prompts, instructions, and skills. Instead of manually configuring each AI assistant (like GitHub Copilot or OpenCode) separately, you define your artifacts once in a canonical location (`.agents/`) and let the tool generate the necessary configuration files for each target.

### Supported Targets

- **OpenCode**: Generates `opencode.json` configuration.
- **GitHub Copilot (VS Code)**: Generates bridge files in `.github/` (prompts, agents, instructions).
- **GitHub Copilot CLI**: Generates bridge files compatible with the CLI.

## Key Principles

- **No Duplication**: Generated files point to your canonical content; they don't copy it.
- **Config-Driven**: A central `manifest.yaml` controls what gets generated.
- **Idempotency**: Running `sync` multiple times produces the same result.
