"""Manifest loading, saving, and validation."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from agent_scaffold.models import (
    ArtifactsConfig,
    CopilotTarget,
    Manifest,
    OpenCodeTarget,
    PathsConfig,
    ProjectConfig,
)

# Constants
MANIFEST_YAML = ".agents/manifest.yaml"
MANIFEST_JSON = ".agents/manifest.json"


class ManifestError(Exception):
    """Error related to manifest operations."""

    pass


class ManifestNotFoundError(ManifestError):
    """Manifest file not found."""

    pass


class ManifestValidationError(ManifestError):
    """Manifest validation failed."""

    pass


def find_manifest(root: Path) -> Path | None:
    """Find the manifest file, preferring YAML over JSON.

    Args:
        root: Project root directory

    Returns:
        Path to manifest file, or None if not found
    """
    yaml_path = root / MANIFEST_YAML
    json_path = root / MANIFEST_JSON

    if yaml_path.exists():
        return yaml_path
    elif json_path.exists():
        return json_path
    return None


def load_manifest(root: Path) -> Manifest:
    """Load and validate the manifest from disk.

    Args:
        root: Project root directory

    Returns:
        Validated Manifest object

    Raises:
        ManifestNotFoundError: If no manifest file exists
        ManifestValidationError: If manifest fails validation
    """
    manifest_path = find_manifest(root)
    if manifest_path is None:
        raise ManifestNotFoundError(
            f"No manifest found. Expected {MANIFEST_YAML} or {MANIFEST_JSON}. "
            "Run 'agent-scaffold init' to create one."
        )

    try:
        content = manifest_path.read_text(encoding="utf-8")
        if manifest_path.suffix == ".yaml" or manifest_path.suffix == ".yml":
            data = yaml.safe_load(content)
        else:
            import json

            data = json.loads(content)

        return Manifest.model_validate(data)

    except yaml.YAMLError as e:
        raise ManifestValidationError(f"Invalid YAML in manifest: {e}") from e
    except ValidationError as e:
        raise ManifestValidationError(f"Manifest validation failed:\n{e}") from e


def save_manifest(root: Path, manifest: Manifest) -> Path:
    """Save the manifest to disk as YAML.

    Args:
        root: Project root directory
        manifest: Manifest object to save

    Returns:
        Path to saved manifest file
    """
    manifest_path = root / MANIFEST_YAML

    # Ensure .agents directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict using aliases for YAML keys
    # Use mode="json" to ensure enums are serialized as strings, not Python objects
    data = manifest.model_dump(by_alias=True, exclude_none=True, mode="json")

    # Custom YAML representer for cleaner output
    def str_representer(dumper: yaml.Dumper, data: str) -> yaml.Node:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_representer)

    content = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )

    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


def create_default_manifest(project_name: str) -> Manifest:
    """Create a new manifest with default configuration.

    Args:
        project_name: Name of the project

    Returns:
        New Manifest object with defaults
    """
    return Manifest(
        schema_version=1,
        project=ProjectConfig(
            name=project_name,
            description=f"Multi-agent configuration for {project_name}",
            default_targets=["opencode", "copilot-vscode", "copilot-cli"],
        ),
        paths=PathsConfig(),
        targets={
            "opencode": OpenCodeTarget(
                kind="opencode",
                enabled=True,
                config_file="opencode.json",
                rules_index_file="AGENTS.md",
            ),
            "copilot-vscode": CopilotTarget(
                kind="copilot",
                enabled=True,
                prompts_dir=".github/prompts",
                agents_dir=".github/agents",
                instructions_dir=".github/instructions",
                repo_instructions_file=".github/copilot-instructions.md",
                skills_dir=".github/skills",
            ),
            "copilot-cli": CopilotTarget(
                kind="copilot",
                enabled=True,
                prompts_dir=None,  # CLI doesn't use prompts
                agents_dir=".github/agents",
                instructions_dir=".github/instructions",
                repo_instructions_file=".github/copilot-instructions.md",
                skills_dir=".github/skills",
            ),
        },
        artifacts=ArtifactsConfig(),
    )
