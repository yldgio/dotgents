# Implementation Guide: agent-scaffold

> **Version:** 0.1.0 (MVP)  
> **Package Manager:** uv  
> **Distribution:** GitHub (via uvx)  
> **Python:** >=3.10

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Phase 1: Project Setup](#phase-1-project-setup)
4. [Phase 2: Core Models](#phase-2-core-models)
5. [Phase 3: Manifest Handling](#phase-3-manifest-handling)
6. [Phase 4: CLI Commands](#phase-4-cli-commands)
7. [Phase 5: Generators](#phase-5-generators)
8. [Phase 6: Sync Command](#phase-6-sync-command)
9. [Phase 7: Doctor Command](#phase-7-doctor-command)
10. [Phase 8: Testing](#phase-8-testing)
11. [Implementation Order](#implementation-order)

---

## Overview

**agent-scaffold** is a CLI tool that maintains a single source of truth for AI coding assistant configurations under `.agents/`, generating target-specific files for:

- **OpenCode** - Config-driven via `opencode.json` with `{file:...}` references
- **GitHub Copilot VS Code** - Bridge files under `.github/`
- **GitHub Copilot CLI** - Shares `.github/` with VS Code (no prompt files)

### Key Principles

1. **No content duplication** - Generated files contain pointers, not copies
2. **Config-driven** - Central manifest drives all generation
3. **Idempotent sync** - Running `sync` repeatedly produces identical output
4. **Deterministic IDs** - Kebab-case IDs used for filenames

---

## Project Structure

```
multi-agent-scaffold/
├── pyproject.toml              # uv/pip package configuration
├── src/
│   └── agent_scaffold/
│       ├── __init__.py         # Package version and exports
│       ├── cli.py              # Click CLI entry point
│       ├── manifest.py         # Manifest loading/parsing/validation
│       ├── models.py           # Pydantic models for manifest schema
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py         # init command
│       │   ├── add.py          # add-* commands
│       │   ├── sync.py         # sync command
│       │   └── doctor.py       # doctor command
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract generator interface
│       │   ├── opencode.py     # OpenCode target generator
│       │   └── copilot.py      # Copilot (VS Code + CLI) generator
│       ├── templates/          # Jinja2 templates for generated files
│       │   ├── opencode_json.j2
│       │   ├── agents_md.j2
│       │   ├── copilot_prompt.md.j2
│       │   ├── copilot_agent.md.j2
│       │   ├── copilot_instruction.md.j2
│       │   ├── copilot_repo_instructions.md.j2
│       │   └── copilot_skill.md.j2
│       └── utils.py            # Helper functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_models.py
│   ├── test_manifest.py
│   ├── test_commands.py
│   └── test_generators.py
├── AGENTS.md                   # Project architecture (existing)
├── IMPLEMENTATION.md           # This file
├── agent-scaffold-plan.md      # Original plan (existing)
└── README.md
```

---

## Phase 1: Project Setup

### 1.1 pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "agent-scaffold"
version = "0.1.0"
description = "Multi-agent scaffold for AI coding assistants"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "jinja2>=3.1.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
agent-scaffold = "agent_scaffold.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_scaffold"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
```

### 1.2 Installation Commands

```bash
# Development install
uv pip install -e ".[dev]"

# Run from GitHub via uvx
uvx --from git+https://github.com/yldgio/dotgents agent-scaffold <command>

# Install from GitHub
uv pip install git+https://github.com/yldgio/dotgents
```

---

## Phase 2: Core Models

### 2.1 Pydantic Models (`models.py`)

Define models matching manifest schema v1:

#### Enums

```python
class TargetKind(str, Enum):
    OPENCODE = "opencode"
    COPILOT = "copilot"

class InstructionScope(str, Enum):
    REPO = "repo"
    PATH = "path"
```

#### Target Override Models

```python
class OpenCodeTargetOverride(BaseModel):
    enabled: bool = True
    name: Optional[str] = None
    mode: Optional[str] = None  # primary|subagent|all
    model: Optional[str] = None
    temperature: Optional[float] = None
    permission: Optional[str] = None
    hidden: Optional[bool] = None
    steps: Optional[int] = None

class CopilotTargetOverride(BaseModel):
    enabled: bool = True
    frontmatter: dict[str, Any] = Field(default_factory=dict)
    out_file: Optional[str] = Field(None, alias="outFile")
    stub_mode: str = Field("link", alias="stubMode")
```

#### Artifact Models

| Model | Required Fields | Optional Fields |
|-------|-----------------|-----------------|
| `PromptArtifact` | id, title, canonicalFile | description, defaultAgent, defaultModel, tools, targets |
| `AgentArtifact` | id, description | promptFile, prompt, targets |
| `InstructionArtifact` | id, scope, canonicalFile | applyTo (required if scope=path), targets |
| `SkillArtifact` | id, canonicalDir, skillFile | assets, targets |

#### Top-Level Models

```python
class Manifest(BaseModel):
    schema_version: int = Field(1, alias="schemaVersion")
    project: ProjectConfig
    paths: PathsConfig = Field(default_factory=PathsConfig)
    targets: dict[str, OpenCodeTarget | CopilotTarget] = Field(default_factory=dict)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
```

---

## Phase 3: Manifest Handling

### 3.1 Manifest Module (`manifest.py`)

```python
def load_manifest(root: Path) -> Manifest:
    """Load manifest from .agents/manifest.yaml or .agents/manifest.json"""
    
def save_manifest(root: Path, manifest: Manifest) -> None:
    """Save manifest to .agents/manifest.yaml"""
    
def find_manifest(root: Path) -> Path | None:
    """Find manifest file, preferring YAML over JSON"""
```

### 3.2 File Priority

1. `.agents/manifest.yaml` (preferred)
2. `.agents/manifest.json` (fallback)

---

## Phase 4: CLI Commands

### 4.1 Command Summary

| Command | Description |
|---------|-------------|
| `init` | Create `.agents/` structure and initial manifest |
| `add-prompt <id>` | Add a new prompt artifact |
| `add-agent <id>` | Add a new agent artifact |
| `add-instruction <id>` | Add a new instruction artifact |
| `add-skill <id>` | Add a new skill artifact |
| `sync` | Generate all target files from manifest |
| `doctor` | Validate manifest and file integrity |

### 4.2 `init` Command

**Purpose:** Bootstrap a new `.agents/` directory

**Behavior:**
1. Check if `.agents/manifest.yaml` exists (abort unless `--force`)
2. Create directories:
   - `.agents/prompts/`
   - `.agents/agents/`
   - `.agents/instructions/`
   - `.agents/skills/`
3. Create `manifest.yaml` with defaults
4. Create sample `repo-default.md` instruction

**Options:**
- `--name <name>`: Project name (default: directory name)
- `--force`: Overwrite existing manifest

### 4.3 `add-*` Commands

All `add-*` commands follow this pattern:

1. Validate ID is kebab-case
2. Check artifact doesn't already exist
3. Create canonical file with template
4. Add entry to manifest
5. Save manifest
6. Print success message

#### `add-prompt <id>`

```bash
agent-scaffold add-prompt explain-code --title "Explain Code" --agent ask
```

Creates:
- `.agents/prompts/explain-code.md`
- Entry in `artifacts.prompts[]`

#### `add-agent <id>`

```bash
agent-scaffold add-agent reviewer --description "Code review specialist"
```

Creates:
- `.agents/agents/reviewer.md`
- Entry in `artifacts.agents[]`

#### `add-instruction <id>`

```bash
agent-scaffold add-instruction typescript --scope path --apply-to "**/*.ts"
```

Creates:
- `.agents/instructions/typescript.md`
- Entry in `artifacts.instructions[]`

#### `add-skill <id>`

```bash
agent-scaffold add-skill api-builder
```

Creates:
- `.agents/skills/api-builder/SKILL.md`
- Entry in `artifacts.skills[]`

---

## Phase 5: Generators

### 5.1 Base Generator

```python
class BaseGenerator(ABC):
    def __init__(self, manifest: Manifest, root: Path):
        self.manifest = manifest
        self.root = root
    
    @abstractmethod
    def generate(self) -> list[Path]:
        """Generate target files, return list of generated paths."""
    
    @abstractmethod
    def list_generated_files(self) -> list[Path]:
        """List all files this generator would create."""
    
    def banner(self, style: str = "html") -> str:
        """Return generated-by banner comment."""
```

### 5.2 OpenCode Generator

**Generates:**

1. `opencode.json`:
   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "instructions": [".agents/instructions/**/*.md"],
     "agent.reviewer": {
       "prompt": {"file": "./.agents/agents/reviewer.md"}
     }
   }
   ```

2. `AGENTS.md` (rules index):
   ```markdown
   # AGENTS.md
   
   > Generated by agent-scaffold. See `.agents/manifest.yaml` for configuration.
   
   ## Instructions
   - [repo-default](.agents/instructions/repo-default.md)
   ```

### 5.3 Copilot Generator

**For copilot-vscode, generates:**

1. `.github/prompts/<id>.prompt.md`:
   ```markdown
   ---
   name: explain-code
   description: Explain the selected code
   agent: ask
   ---
   
   Follow instructions in '.agents/prompts/explain-code.md'.
   
   See: [explain-code](../../.agents/prompts/explain-code.md)
   ```

2. `.github/agents/<id>.agent.md`:
   ```markdown
   ---
   name: reviewer
   description: Code review specialist
   ---
   
   Follow instructions in '.agents/agents/reviewer.md'.
   
   See: [reviewer](../../.agents/agents/reviewer.md)
   ```

3. `.github/instructions/<id>.instructions.md`:
   ```markdown
   ---
   applyTo: "**/*.ts"
   ---
   
   Follow instructions in '.agents/instructions/typescript.md'.
   
   See: [typescript](../../.agents/instructions/typescript.md)
   ```

4. `.github/copilot-instructions.md`:
   ```markdown
   <!-- Generated by agent-scaffold -->
   
   Follow instructions in '.agents/instructions/repo-default.md'.
   
   See: [repo-default](../../.agents/instructions/repo-default.md)
   ```

5. `.github/skills/<id>/SKILL.md`:
   ```markdown
   ---
   name: api-builder
   description: API builder skill
   ---
   
   Follow instructions in '.agents/skills/api-builder/SKILL.md'.
   
   See: [api-builder](../../.agents/skills/api-builder/SKILL.md)
   ```

**For copilot-cli:**
- Same as above, but **skip prompt files** (IDE-only feature)

---

## Phase 6: Sync Command

### 6.1 Behavior

```bash
agent-scaffold sync [--prune] [--dry-run] [--target <target>]
```

1. Load and validate manifest
2. For each enabled target, invoke generator
3. Write all generated files
4. Track generated files in `.agents/.generated.json`
5. Report results

### 6.2 Options

| Option | Description |
|--------|-------------|
| `--prune` | Remove files no longer in manifest |
| `--dry-run` | Show what would be generated |
| `--target <t>` | Only sync specific target |

### 6.3 Generated File Tracking

`.agents/.generated.json`:
```json
{
  "version": 1,
  "files": [
    ".github/prompts/explain-code.prompt.md",
    ".github/agents/reviewer.agent.md",
    "opencode.json"
  ]
}
```

---

## Phase 7: Doctor Command

### 7.1 Validations

| Check | Description |
|-------|-------------|
| Manifest exists | `.agents/manifest.yaml` or `.json` present |
| Schema valid | Manifest parses against Pydantic models |
| Files exist | All `canonicalFile`/`promptFile`/`skillFile` paths exist |
| IDs unique | No duplicate IDs within artifact types |
| IDs kebab-case | All IDs follow `[a-z0-9-]+` pattern |
| Targets valid | Referenced targets exist in config |
| Path scope | Path-scoped instructions have `applyTo` |

### 7.2 Output

Use Rich to display results:

```
✓ Manifest exists
✓ Schema valid
✓ All canonical files exist
✓ IDs are unique
✗ Invalid ID: "MyAgent" (must be kebab-case)
```

---

## Phase 8: Testing

### 8.1 Test Structure

```
tests/
├── conftest.py          # Fixtures
├── test_models.py       # Pydantic model validation
├── test_manifest.py     # Manifest load/save
├── test_commands.py     # CLI command behavior
└── test_generators.py   # Generator output
```

### 8.2 Key Fixtures

```python
@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create temporary project with .agents/ structure."""

@pytest.fixture
def sample_manifest() -> Manifest:
    """Pre-populated manifest for testing."""
```

---

## Implementation Order

Execute phases in this order for incremental testability:

| Step | Component | Description | Est. Time |
|------|-----------|-------------|-----------|
| 1 | Project setup | pyproject.toml, directories, basic CLI | 30 min |
| 2 | `models.py` | Pydantic models for manifest | 1 hr |
| 3 | `manifest.py` | Load/save manifest | 30 min |
| 4 | `init` command | Create .agents/ structure | 30 min |
| 5 | `add-prompt` | First add command | 30 min |
| 6 | `add-agent` | Agent artifacts | 20 min |
| 7 | `add-instruction` | Instruction artifacts | 20 min |
| 8 | `add-skill` | Skill artifacts | 20 min |
| 9 | Base generator | Abstract interface | 20 min |
| 10 | OpenCode generator | opencode.json + AGENTS.md | 45 min |
| 11 | Copilot generator | .github/ files | 1 hr |
| 12 | `sync` command | Orchestrate generators | 30 min |
| 13 | `doctor` command | Validation checks | 45 min |
| 14 | `--prune` support | Track/remove stale files | 30 min |
| 15 | Tests | Full test coverage | 2 hr |

**Total estimated time:** ~9 hours

---

## Notes

### Generated File Banner

Every generated file must start with:

```markdown
<!-- Generated by agent-scaffold. Do not edit manually. -->
```

Or for JSON:
```json
// Generated by agent-scaffold. Do not edit manually.
```

### Stable Ordering

Always sort artifacts by `id` when generating to ensure deterministic output.

### Path Handling

Use `pathlib.Path` for all file operations (cross-platform compatibility).

### Future Targets

The architecture supports adding new targets (Claude Code, Gemini CLI) by:
1. Adding target config model
2. Implementing new generator class
3. Registering in sync command
