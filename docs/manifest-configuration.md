# Manifest Configuration

The `.agents/manifest.yaml` file is the heart of Agent Scaffold. It defines your project configuration, active targets, and the inventory of all artifacts.

## Schema Version

```yaml
schemaVersion: 1
```

## Project Config

```yaml
project:
  name: my-project
  description: Multi-agent setup
  defaultTargets:
    - opencode
    - copilot-vscode
    - copilot-cli
```

## Paths Config

Start mapping of canonical directories. Ususally you don't need to change these.

```yaml
paths:
  promptsDir: .agents/prompts
  agentsDir: .agents/agents
  instructionsDir: .agents/instructions
  skillsDir: .agents/skills
```

## Targets Config

Configures the output targets. You can enable/disable targets here.

```yaml
targets:
  opencode:
    kind: opencode
    enabled: true
    configFile: opencode.json
    rulesIndexFile: AGENTS.md

  copilot-vscode:
    kind: copilot
    enabled: true
    promptsDir: .github/prompts
    agentsDir: .github/agents
    # ... other Copilot specific paths
```

## Artifacts Config

This section lists all your content. While you can edit this manually, we recommend using the `add-*` CLI commands to ensure consistency.

### `artifacts.prompts`

```yaml
- id: explain-code
  title: Explain Code
  canonicalFile: .agents/prompts/explain-code.md
  description: ...
  defaultAgent: ask
  targets: 
    copilot-vscode:
      enabled: true
      frontmatter: 
        model: gpt-4
```

### `artifacts.agents`

```yaml
- id: reviewer
  description: Code review agent
  promptFile: .agents/agents/reviewer.md
  targets:
    opencode:
      enabled: true
      mode: subagent
```

### `artifacts.instructions`

```yaml
- id: typescript-rules
  scope: path
  canonicalFile: .agents/instructions/typescript.md
  applyTo: "**/*.ts"
```

### `artifacts.skills`

```yaml
- id: data-processor
  canonicalDir: .agents/skills/data-processor
  skillFile: .agents/skills/data-processor/SKILL.md
```
