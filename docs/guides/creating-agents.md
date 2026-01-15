# Creating Agents

Agents are specialized personas that can help you with specific tasks. In Agent Scaffold, you define an agent once, and it becomes available to all supported AI assistants.

## 1. The `add-agent` Command

To create a new agent, use the CLI:

```bash
agent-scaffold add-agent my-agent --description "Description of what this agent does"
```

This performs two actions:
1. Adds an entry to `artifacts.agents` in `manifest.yaml`.
2. Creates a Markdown file at `.agents/agents/my-agent.md`.

## 2. Defining the Agent Persona

Open the generated file `.agents/agents/my-agent.md`. This files serves as the **System Prompt** for your agent. You should describe:
- Who the agent is (e.g., "You are an expert Python debugger").
- Its specific capabilities.
- Its tone and style.
- Any specific rules it must follow.

**Example Content:**

```markdown
You are the **QA Engineer Agent**. 

Your responsibility is to review code for potential bugs, security vulnerabilities, and logic errors.
When reviewing code:
- Be thorough and strict.
- Provide code snippets to fix issues.
- Always explain *why* something is a bug.
```

## 3. Configuring Target-Specific Options

By default, an agent is enabled for all targets. You can customize this in `manifest.yaml`.

```yaml
- id: my-agent
  targets:
    opencode:
      enabled: true
      mode: subagent # Run as a sub-agent vs main agent
    copilot:
      enabled: false # Disable for Copilot
```

## 4. Syncing

After editing your agent definition, run:

```bash
agent-scaffold sync
```

This will generate:
- A `.github/agents/my-agent.agent.md` file (for Copilot).
- An entry in `opencode.json` (for OpenCode).
