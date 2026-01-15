"""Pydantic models for the manifest schema v1."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TargetKind(str, Enum):
    """Supported target types."""

    OPENCODE = "opencode"
    COPILOT = "copilot"


class InstructionScope(str, Enum):
    """Instruction scope types."""

    REPO = "repo"
    PATH = "path"


# =============================================================================
# Target Override Models (per-artifact target configuration)
# =============================================================================


class OpenCodeTargetOverride(BaseModel):
    """OpenCode-specific overrides for an artifact."""

    model_config = ConfigDict(populate_by_name=True)

    enabled: bool = True
    name: str | None = None
    mode: str | None = None  # primary|subagent|all
    model: str | None = None
    temperature: float | None = None
    permission: str | None = None
    hidden: bool | None = None
    steps: int | None = None


class CopilotTargetOverride(BaseModel):
    """Copilot-specific overrides for an artifact."""

    model_config = ConfigDict(populate_by_name=True)

    enabled: bool = True
    frontmatter: dict[str, Any] = Field(default_factory=dict)
    out_file: str | None = Field(None, alias="outFile")
    stub_mode: str = Field("link", alias="stubMode")


# =============================================================================
# Artifact Models
# =============================================================================


class PromptArtifact(BaseModel):
    """A prompt artifact (primarily for Copilot VS Code)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    canonical_file: str = Field(alias="canonicalFile")
    description: str | None = None
    default_agent: str | None = Field(None, alias="defaultAgent")
    default_model: str | None = Field(None, alias="defaultModel")
    tools: list[str] = Field(default_factory=list)
    targets: dict[str, CopilotTargetOverride] = Field(default_factory=dict)


class AgentArtifact(BaseModel):
    """An agent artifact (for OpenCode and Copilot)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    description: str
    prompt_file: str | None = Field(None, alias="promptFile")
    prompt: str | None = None
    targets: dict[str, OpenCodeTargetOverride | CopilotTargetOverride] = Field(
        default_factory=dict
    )


class InstructionArtifact(BaseModel):
    """An instruction artifact (repo-wide or path-scoped)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    scope: InstructionScope
    canonical_file: str = Field(alias="canonicalFile")
    apply_to: str | None = Field(None, alias="applyTo")
    targets: dict[str, CopilotTargetOverride | OpenCodeTargetOverride] = Field(
        default_factory=dict
    )


class SkillArtifact(BaseModel):
    """A skill artifact (skill bundle with SKILL.md)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    canonical_dir: str = Field(alias="canonicalDir")
    skill_file: str = Field(alias="skillFile")
    name: str | None = None
    description: str | None = None
    assets: list[str] = Field(default_factory=list)
    targets: dict[str, CopilotTargetOverride] = Field(default_factory=dict)


class CommandArtifact(BaseModel):
    """OpenCode slash command artifact."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    canonical_file: str = Field(alias="canonicalFile")
    description: str = ""
    user_input: Literal["required", "optional", "none"] = Field(
        default="optional",
        alias="userInput",
    )
    targets: dict[str, OpenCodeTargetOverride] = Field(default_factory=dict)


# =============================================================================
# Target Configuration Models
# =============================================================================


class OpenCodeTarget(BaseModel):
    """OpenCode target configuration."""

    model_config = ConfigDict(populate_by_name=True)

    kind: TargetKind = TargetKind.OPENCODE
    enabled: bool = True
    config_file: str = Field("opencode.json", alias="configFile")
    rules_index_file: str = Field("AGENTS.md", alias="rulesIndexFile")


class CopilotTarget(BaseModel):
    """Copilot target configuration (VS Code or CLI)."""

    model_config = ConfigDict(populate_by_name=True)

    kind: TargetKind = TargetKind.COPILOT
    enabled: bool = True
    prompts_dir: str | None = Field(None, alias="promptsDir")
    agents_dir: str = Field(".github/agents", alias="agentsDir")
    instructions_dir: str = Field(".github/instructions", alias="instructionsDir")
    repo_instructions_file: str = Field(
        ".github/copilot-instructions.md", alias="repoInstructionsFile"
    )
    skills_dir: str = Field(".github/skills", alias="skillsDir")


# =============================================================================
# Top-Level Configuration Models
# =============================================================================


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str = ""
    default_targets: list[str] = Field(
        default_factory=lambda: ["opencode", "copilot-vscode", "copilot-cli"],
        alias="defaultTargets",
    )


class PathsConfig(BaseModel):
    """Canonical paths configuration."""

    model_config = ConfigDict(populate_by_name=True)

    prompts_dir: str = Field(".agents/prompts", alias="promptsDir")
    commands_dir: str = Field(".agents/commands", alias="commandsDir")
    agents_dir: str = Field(".agents/agents", alias="agentsDir")
    instructions_dir: str = Field(".agents/instructions", alias="instructionsDir")
    skills_dir: str = Field(".agents/skills", alias="skillsDir")


class ArtifactsConfig(BaseModel):
    """Container for all artifact definitions."""

    prompts: list[PromptArtifact] = Field(default_factory=list)
    agents: list[AgentArtifact] = Field(default_factory=list)
    instructions: list[InstructionArtifact] = Field(default_factory=list)
    skills: list[SkillArtifact] = Field(default_factory=list)
    commands: list[CommandArtifact] = Field(default_factory=list)


class Manifest(BaseModel):
    """The root manifest schema (v1)."""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(1, alias="schemaVersion")
    project: ProjectConfig
    paths: PathsConfig = Field(default_factory=PathsConfig)
    targets: dict[str, OpenCodeTarget | CopilotTarget] = Field(default_factory=dict)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
