"""Pytest fixtures for agent-scaffold tests."""

from pathlib import Path

import pytest

from agent_scaffold.manifest import create_default_manifest, save_manifest
from agent_scaffold.models import (
    AgentArtifact,
    CopilotTargetOverride,
    InstructionArtifact,
    InstructionScope,
    OpenCodeTargetOverride,
    PromptArtifact,
    SkillArtifact,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project with .agents/ structure."""
    agents_dir = tmp_path / ".agents"
    (agents_dir / "prompts").mkdir(parents=True)
    (agents_dir / "agents").mkdir(parents=True)
    (agents_dir / "instructions").mkdir(parents=True)
    (agents_dir / "skills").mkdir(parents=True)

    # Create a default manifest
    manifest = create_default_manifest("test-project")
    save_manifest(tmp_path, manifest)

    return tmp_path


@pytest.fixture
def sample_manifest(tmp_project: Path):
    """Create a sample manifest with some artifacts."""
    from agent_scaffold.manifest import load_manifest, save_manifest

    manifest = load_manifest(tmp_project)

    # Add a prompt
    prompt_file = tmp_project / ".agents/prompts/explain-code.md"
    prompt_file.write_text("# Explain Code\n\nExplain the selected code.")
    manifest.artifacts.prompts.append(
        PromptArtifact(
            id="explain-code",
            title="Explain Code",
            canonical_file=".agents/prompts/explain-code.md",
            description="Explain the selected code",
            default_agent="ask",
            targets={
                "copilot-vscode": CopilotTargetOverride(
                    enabled=True,
                    frontmatter={"name": "explain-code", "description": "Explain code"},
                ),
            },
        )
    )

    # Add an agent
    agent_file = tmp_project / ".agents/agents/reviewer.md"
    agent_file.write_text("# Reviewer Agent\n\nReviews code for issues.")
    manifest.artifacts.agents.append(
        AgentArtifact(
            id="reviewer",
            description="Code review specialist",
            prompt_file=".agents/agents/reviewer.md",
            targets={
                "opencode": OpenCodeTargetOverride(enabled=True),
                "copilot-vscode": CopilotTargetOverride(
                    enabled=True,
                    frontmatter={"name": "reviewer", "description": "Code review specialist"},
                ),
                "copilot-cli": CopilotTargetOverride(
                    enabled=True,
                    frontmatter={"name": "reviewer", "description": "Code review specialist"},
                ),
            },
        )
    )

    # Add an instruction
    instruction_file = tmp_project / ".agents/instructions/typescript.md"
    instruction_file.write_text("# TypeScript Guidelines\n\nUse strict mode.")
    manifest.artifacts.instructions.append(
        InstructionArtifact(
            id="typescript",
            scope=InstructionScope.PATH,
            canonical_file=".agents/instructions/typescript.md",
            apply_to="**/*.ts",
            targets={
                "copilot-vscode": CopilotTargetOverride(enabled=True),
                "copilot-cli": CopilotTargetOverride(enabled=True),
            },
        )
    )

    # Add a skill
    skill_dir = tmp_project / ".agents/skills/api-builder"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: API Builder\ndescription: Build APIs\n---\n\n# API Builder")
    manifest.artifacts.skills.append(
        SkillArtifact(
            id="api-builder",
            canonical_dir=".agents/skills/api-builder",
            skill_file=".agents/skills/api-builder/SKILL.md",
            name="API Builder",
            description="Build APIs quickly",
            targets={
                "copilot-vscode": CopilotTargetOverride(enabled=True),
                "copilot-cli": CopilotTargetOverride(enabled=True),
            },
        )
    )

    save_manifest(tmp_project, manifest)
    return manifest
