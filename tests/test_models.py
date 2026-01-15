"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from agent_scaffold.models import (
    AgentArtifact,
    ArtifactsConfig,
    CopilotTarget,
    CopilotTargetOverride,
    InstructionArtifact,
    InstructionScope,
    Manifest,
    OpenCodeTarget,
    OpenCodeTargetOverride,
    PathsConfig,
    ProjectConfig,
    PromptArtifact,
    SkillArtifact,
    TargetKind,
)


class TestEnums:
    """Tests for enum definitions."""

    def test_target_kind_values(self):
        assert TargetKind.OPENCODE.value == "opencode"
        assert TargetKind.COPILOT.value == "copilot"

    def test_instruction_scope_values(self):
        assert InstructionScope.REPO.value == "repo"
        assert InstructionScope.PATH.value == "path"


class TestTargetOverrideModels:
    """Tests for target override models."""

    def test_opencode_override_defaults(self):
        override = OpenCodeTargetOverride()
        assert override.enabled is True
        assert override.name is None
        assert override.mode is None
        assert override.model is None
        assert override.temperature is None
        assert override.permission is None
        assert override.hidden is None
        assert override.steps is None

    def test_opencode_override_with_values(self):
        override = OpenCodeTargetOverride(
            enabled=False,
            name="custom-agent",
            mode="primary",
            model="gpt-4",
            temperature=0.7,
            permission="read",
            hidden=True,
            steps=5,
        )
        assert override.enabled is False
        assert override.name == "custom-agent"
        assert override.mode == "primary"
        assert override.model == "gpt-4"
        assert override.temperature == 0.7
        assert override.permission == "read"
        assert override.hidden is True
        assert override.steps == 5

    def test_copilot_override_defaults(self):
        override = CopilotTargetOverride()
        assert override.enabled is True
        assert override.frontmatter == {}
        assert override.out_file is None
        assert override.stub_mode == "link"

    def test_copilot_override_with_alias(self):
        # Test that aliases work when parsing dict
        data = {
            "enabled": True,
            "frontmatter": {"name": "test"},
            "outFile": "custom.md",
            "stubMode": "inline",
        }
        override = CopilotTargetOverride.model_validate(data)
        assert override.out_file == "custom.md"
        assert override.stub_mode == "inline"


class TestArtifactModels:
    """Tests for artifact models."""

    def test_prompt_artifact_required_fields(self):
        with pytest.raises(ValidationError):
            PromptArtifact()

    def test_prompt_artifact_minimal(self):
        prompt = PromptArtifact(
            id="explain-code",
            title="Explain Code",
            canonical_file=".agents/prompts/explain-code.md",
        )
        assert prompt.id == "explain-code"
        assert prompt.title == "Explain Code"
        assert prompt.canonical_file == ".agents/prompts/explain-code.md"
        assert prompt.description is None
        assert prompt.default_agent is None
        assert prompt.tools == []

    def test_prompt_artifact_with_alias(self):
        data = {
            "id": "test",
            "title": "Test",
            "canonicalFile": ".agents/prompts/test.md",
            "defaultAgent": "ask",
            "defaultModel": "gpt-4",
        }
        prompt = PromptArtifact.model_validate(data)
        assert prompt.canonical_file == ".agents/prompts/test.md"
        assert prompt.default_agent == "ask"
        assert prompt.default_model == "gpt-4"

    def test_agent_artifact_minimal(self):
        agent = AgentArtifact(
            id="reviewer",
            description="Code review specialist",
        )
        assert agent.id == "reviewer"
        assert agent.description == "Code review specialist"
        assert agent.prompt_file is None
        assert agent.prompt is None

    def test_agent_artifact_with_prompt_file(self):
        data = {
            "id": "reviewer",
            "description": "Code review specialist",
            "promptFile": ".agents/agents/reviewer.md",
        }
        agent = AgentArtifact.model_validate(data)
        assert agent.prompt_file == ".agents/agents/reviewer.md"

    def test_instruction_artifact_repo_scope(self):
        instruction = InstructionArtifact(
            id="repo-default",
            scope=InstructionScope.REPO,
            canonical_file=".agents/instructions/repo-default.md",
        )
        assert instruction.id == "repo-default"
        assert instruction.scope == InstructionScope.REPO
        assert instruction.apply_to is None

    def test_instruction_artifact_path_scope(self):
        data = {
            "id": "typescript",
            "scope": "path",
            "canonicalFile": ".agents/instructions/typescript.md",
            "applyTo": "**/*.ts",
        }
        instruction = InstructionArtifact.model_validate(data)
        assert instruction.scope == InstructionScope.PATH
        assert instruction.apply_to == "**/*.ts"

    def test_skill_artifact_minimal(self):
        skill = SkillArtifact(
            id="api-builder",
            canonical_dir=".agents/skills/api-builder",
            skill_file=".agents/skills/api-builder/SKILL.md",
        )
        assert skill.id == "api-builder"
        assert skill.canonical_dir == ".agents/skills/api-builder"
        assert skill.skill_file == ".agents/skills/api-builder/SKILL.md"
        assert skill.assets == []


class TestTargetModels:
    """Tests for target configuration models."""

    def test_opencode_target_defaults(self):
        target = OpenCodeTarget()
        assert target.kind == TargetKind.OPENCODE
        assert target.enabled is True
        assert target.config_file == "opencode.json"
        assert target.rules_index_file == "AGENTS.md"

    def test_opencode_target_with_alias(self):
        data = {
            "kind": "opencode",
            "enabled": True,
            "configFile": "custom-opencode.json",
            "rulesIndexFile": "RULES.md",
        }
        target = OpenCodeTarget.model_validate(data)
        assert target.config_file == "custom-opencode.json"
        assert target.rules_index_file == "RULES.md"

    def test_copilot_target_defaults(self):
        target = CopilotTarget()
        assert target.kind == TargetKind.COPILOT
        assert target.enabled is True
        assert target.agents_dir == ".github/agents"
        assert target.instructions_dir == ".github/instructions"

    def test_copilot_target_vscode(self):
        data = {
            "kind": "copilot",
            "promptsDir": ".github/prompts",
            "agentsDir": ".github/agents",
        }
        target = CopilotTarget.model_validate(data)
        assert target.prompts_dir == ".github/prompts"

    def test_copilot_target_cli_no_prompts(self):
        data = {
            "kind": "copilot",
            "promptsDir": None,
            "agentsDir": ".github/agents",
        }
        target = CopilotTarget.model_validate(data)
        assert target.prompts_dir is None


class TestTopLevelModels:
    """Tests for top-level configuration models."""

    def test_project_config_minimal(self):
        project = ProjectConfig(name="my-project")
        assert project.name == "my-project"
        assert project.description == ""
        assert project.default_targets == ["opencode", "copilot-vscode", "copilot-cli"]

    def test_project_config_with_defaults(self):
        data = {
            "name": "my-project",
            "description": "A test project",
            "defaultTargets": ["opencode"],
        }
        project = ProjectConfig.model_validate(data)
        assert project.default_targets == ["opencode"]

    def test_paths_config_defaults(self):
        paths = PathsConfig()
        assert paths.prompts_dir == ".agents/prompts"
        assert paths.commands_dir == ".agents/commands"
        assert paths.agents_dir == ".agents/agents"
        assert paths.instructions_dir == ".agents/instructions"
        assert paths.skills_dir == ".agents/skills"

    def test_artifacts_config_defaults(self):
        artifacts = ArtifactsConfig()
        assert artifacts.prompts == []
        assert artifacts.agents == []
        assert artifacts.instructions == []
        assert artifacts.skills == []

    def test_manifest_minimal(self):
        manifest = Manifest(
            project=ProjectConfig(name="test-project"),
        )
        assert manifest.schema_version == 1
        assert manifest.project.name == "test-project"
        assert manifest.paths.prompts_dir == ".agents/prompts"
        assert manifest.targets == {}
        assert manifest.artifacts.prompts == []

    def test_manifest_with_alias(self):
        data = {
            "schemaVersion": 2,
            "project": {"name": "test-project"},
            "paths": {"promptsDir": "custom/prompts"},
            "targets": {
                "opencode": {"kind": "opencode", "enabled": True},
            },
            "artifacts": {
                "prompts": [
                    {
                        "id": "test",
                        "title": "Test",
                        "canonicalFile": "custom/prompts/test.md",
                    }
                ]
            },
        }
        manifest = Manifest.model_validate(data)
        assert manifest.schema_version == 2
        assert manifest.paths.prompts_dir == "custom/prompts"
        assert len(manifest.artifacts.prompts) == 1


class TestModelSerialization:
    """Tests for model serialization."""

    def test_manifest_serialize_with_aliases(self):
        manifest = Manifest(
            project=ProjectConfig(name="test-project"),
        )
        data = manifest.model_dump(by_alias=True, exclude_none=True)
        assert "schemaVersion" in data
        assert data["schemaVersion"] == 1
        assert "project" in data
        assert data["project"]["name"] == "test-project"

    def test_prompt_artifact_serialize(self):
        prompt = PromptArtifact(
            id="test",
            title="Test",
            canonical_file=".agents/prompts/test.md",
            default_agent="ask",
        )
        data = prompt.model_dump(by_alias=True, exclude_none=True)
        assert data["canonicalFile"] == ".agents/prompts/test.md"
        assert data["defaultAgent"] == "ask"
