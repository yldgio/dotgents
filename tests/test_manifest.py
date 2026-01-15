"""Tests for manifest handling."""

import json
from pathlib import Path

import pytest
import yaml

from agent_scaffold.manifest import (
    MANIFEST_JSON,
    MANIFEST_YAML,
    ManifestNotFoundError,
    ManifestValidationError,
    create_default_manifest,
    find_manifest,
    load_manifest,
    save_manifest,
)
from agent_scaffold.models import (
    CopilotTarget,
    InstructionArtifact,
    InstructionScope,
    Manifest,
    OpenCodeTarget,
    ProjectConfig,
    TargetKind,
)


class TestFindManifest:
    """Tests for find_manifest function."""

    def test_find_yaml_manifest(self, tmp_path: Path):
        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text("schemaVersion: 1\nproject:\n  name: test")

        result = find_manifest(tmp_path)
        assert result == manifest_path

    def test_find_json_manifest(self, tmp_path: Path):
        manifest_path = tmp_path / ".agents" / "manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text('{"schemaVersion": 1, "project": {"name": "test"}}')

        result = find_manifest(tmp_path)
        assert result == manifest_path

    def test_yaml_preferred_over_json(self, tmp_path: Path):
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir(parents=True)

        yaml_path = agents_dir / "manifest.yaml"
        json_path = agents_dir / "manifest.json"
        yaml_path.write_text("schemaVersion: 1\nproject:\n  name: yaml-project")
        json_path.write_text('{"schemaVersion": 1, "project": {"name": "json-project"}}')

        result = find_manifest(tmp_path)
        assert result == yaml_path

    def test_no_manifest_found(self, tmp_path: Path):
        result = find_manifest(tmp_path)
        assert result is None


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_yaml_manifest(self, tmp_path: Path):
        manifest_content = """
schemaVersion: 1
project:
  name: test-project
  description: A test project
paths:
  promptsDir: .agents/prompts
targets:
  opencode:
    kind: opencode
    enabled: true
artifacts:
  prompts: []
"""
        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(manifest_content)

        manifest = load_manifest(tmp_path)
        assert manifest.project.name == "test-project"
        assert manifest.project.description == "A test project"
        assert "opencode" in manifest.targets

    def test_load_json_manifest(self, tmp_path: Path):
        manifest_content = {
            "schemaVersion": 1,
            "project": {"name": "json-project"},
            "paths": {},
            "targets": {},
            "artifacts": {},
        }
        manifest_path = tmp_path / ".agents" / "manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest_content))

        manifest = load_manifest(tmp_path)
        assert manifest.project.name == "json-project"

    def test_load_manifest_not_found(self, tmp_path: Path):
        with pytest.raises(ManifestNotFoundError) as exc_info:
            load_manifest(tmp_path)
        assert "No manifest found" in str(exc_info.value)

    def test_load_manifest_invalid_yaml(self, tmp_path: Path):
        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text("invalid: yaml: content: :")

        with pytest.raises(ManifestValidationError) as exc_info:
            load_manifest(tmp_path)
        assert "Invalid YAML" in str(exc_info.value)

    def test_load_manifest_validation_error(self, tmp_path: Path):
        # Missing required 'project' field
        manifest_content = """
schemaVersion: 1
paths: {}
"""
        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(manifest_content)

        with pytest.raises(ManifestValidationError) as exc_info:
            load_manifest(tmp_path)
        assert "validation failed" in str(exc_info.value)


class TestSaveManifest:
    """Tests for save_manifest function."""

    def test_save_manifest_creates_directory(self, tmp_path: Path):
        manifest = Manifest(project=ProjectConfig(name="test-project"))

        result = save_manifest(tmp_path, manifest)

        assert result.exists()
        assert result.parent.name == ".agents"

    def test_save_manifest_yaml_format(self, tmp_path: Path):
        manifest = Manifest(project=ProjectConfig(name="test-project"))

        save_manifest(tmp_path, manifest)

        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        content = manifest_path.read_text()
        data = yaml.safe_load(content)

        assert data["schemaVersion"] == 1
        assert data["project"]["name"] == "test-project"

    def test_save_manifest_uses_aliases(self, tmp_path: Path):
        manifest = Manifest(project=ProjectConfig(name="test-project"))

        save_manifest(tmp_path, manifest)

        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        content = manifest_path.read_text()

        # Check that aliases are used in output
        assert "schemaVersion" in content
        assert "schema_version" not in content

    def test_save_manifest_excludes_none(self, tmp_path: Path):
        manifest = Manifest(project=ProjectConfig(name="test-project"))

        save_manifest(tmp_path, manifest)

        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        content = manifest_path.read_text()
        data = yaml.safe_load(content)

        # None values should be excluded
        assert "description" not in data["project"] or data["project"]["description"] == ""

    def test_save_and_reload_roundtrip(self, tmp_path: Path):
        original = Manifest(
            project=ProjectConfig(name="roundtrip-test", description="Testing roundtrip"),
            targets={
                "opencode": OpenCodeTarget(kind=TargetKind.OPENCODE, enabled=True),
            },
        )

        save_manifest(tmp_path, original)
        reloaded = load_manifest(tmp_path)

        assert reloaded.project.name == original.project.name
        assert reloaded.project.description == original.project.description
        assert "opencode" in reloaded.targets


class TestCreateDefaultManifest:
    """Tests for create_default_manifest function."""

    def test_create_default_manifest_basic(self):
        manifest = create_default_manifest("my-project")

        assert manifest.schema_version == 1
        assert manifest.project.name == "my-project"
        assert "my-project" in manifest.project.description

    def test_create_default_manifest_has_targets(self):
        manifest = create_default_manifest("test")

        assert "opencode" in manifest.targets
        assert "copilot-vscode" in manifest.targets
        assert "copilot-cli" in manifest.targets

    def test_create_default_manifest_opencode_target(self):
        manifest = create_default_manifest("test")
        opencode = manifest.targets["opencode"]

        assert isinstance(opencode, OpenCodeTarget)
        assert opencode.kind == TargetKind.OPENCODE
        assert opencode.enabled is True
        assert opencode.config_file == "opencode.json"

    def test_create_default_manifest_copilot_vscode_target(self):
        manifest = create_default_manifest("test")
        copilot = manifest.targets["copilot-vscode"]

        assert isinstance(copilot, CopilotTarget)
        assert copilot.kind == TargetKind.COPILOT
        assert copilot.prompts_dir == ".github/prompts"  # VS Code has prompts

    def test_create_default_manifest_copilot_cli_target(self):
        manifest = create_default_manifest("test")
        copilot = manifest.targets["copilot-cli"]

        assert isinstance(copilot, CopilotTarget)
        assert copilot.prompts_dir is None  # CLI doesn't have prompts

    def test_create_default_manifest_empty_artifacts(self):
        manifest = create_default_manifest("test")

        assert manifest.artifacts.prompts == []
        assert manifest.artifacts.agents == []
        assert manifest.artifacts.instructions == []
        assert manifest.artifacts.skills == []


class TestManifestWithArtifacts:
    """Tests for manifest with artifacts."""

    def test_load_manifest_with_artifacts(self, tmp_path: Path):
        manifest_content = """
schemaVersion: 1
project:
  name: test-project
paths:
  promptsDir: .agents/prompts
targets: {}
artifacts:
  prompts:
    - id: explain-code
      title: Explain Code
      canonicalFile: .agents/prompts/explain-code.md
  agents:
    - id: reviewer
      description: Code review specialist
      promptFile: .agents/agents/reviewer.md
  instructions:
    - id: typescript
      scope: path
      canonicalFile: .agents/instructions/typescript.md
      applyTo: "**/*.ts"
"""
        manifest_path = tmp_path / ".agents" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(manifest_content)

        manifest = load_manifest(tmp_path)

        assert len(manifest.artifacts.prompts) == 1
        assert manifest.artifacts.prompts[0].id == "explain-code"

        assert len(manifest.artifacts.agents) == 1
        assert manifest.artifacts.agents[0].id == "reviewer"

        assert len(manifest.artifacts.instructions) == 1
        assert manifest.artifacts.instructions[0].scope == InstructionScope.PATH
        assert manifest.artifacts.instructions[0].apply_to == "**/*.ts"

    def test_save_manifest_with_artifacts(self, tmp_path: Path):
        manifest = Manifest(project=ProjectConfig(name="test"))
        manifest.artifacts.instructions.append(
            InstructionArtifact(
                id="repo-default",
                scope=InstructionScope.REPO,
                canonical_file=".agents/instructions/repo-default.md",
            )
        )

        save_manifest(tmp_path, manifest)
        reloaded = load_manifest(tmp_path)

        assert len(reloaded.artifacts.instructions) == 1
        assert reloaded.artifacts.instructions[0].id == "repo-default"
