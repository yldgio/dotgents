# Introduction

Agent Scaffold is a command-line interface (CLI) tool designed to streamline the management of AI coding assistant configurations. In a modern development environment, you might use multiple AI tools (e.g., GitHub Copilot in VS Code, GitHub Copilot CLI, OpenCode), each requiring its own specific configuration format and file structure.

Maintaining consistency across these tools can be challenging. Agent Scaffold solves this by introducing a **Single Source of Truth** architecture.

## How It Works

1.  **Define Once**: You define your agents, prompts, instructions, and skills in a centralized `.agents/` directory using standard Markdown files.
2.  **Configure**: A `manifest.yaml` file defines which artifacts map to which targets.
3.  **Generate**: The `agent-scaffold sync` command generates the specific configuration files and "bridge" files needed by each supported tool.

## Benefits

*   **Consistency**: Ensure all your AI assistants adhere to the same project rules and instructions.
*   **Maintainability**: Update an instruction in one place, and propagate it to all tools with a single command.
*   **Version Control Friendly**: The canonical artifacts are plain text/Markdown, perfect for Git.
*   **Extensible**: designed to support more targets in the future.

## Supported Targets

### OpenCode
Agent Scaffold generates an `opencode.json` file at the root of your repository. This file maps your canonical agents and instructions to OpenCode's configuration format using file references (`{ "file": "..." }`), ensuring OpenCode reads directly from your source files.

### GitHub Copilot (VS Code & CLI)
Agent Scaffold generates a `.github/` directory structure containing "bridge files". These act as pointers. For example, a generated prompt file `.github/prompts/explain.prompt.md` will contain metadata and a reference to your canonical `.agents/prompts/explain.md` file.

This allows Copilot to discover and use your artifacts while keeping the actual content centralized.
