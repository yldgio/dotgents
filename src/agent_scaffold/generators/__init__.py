"""Generators for target-specific files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from agent_scaffold.models import CopilotTarget, Manifest, OpenCodeTarget

if TYPE_CHECKING:
    from agent_scaffold.generators.base import BaseGenerator

# Tracking file for generated files
GENERATED_TRACKING_FILE = ".agents/.generated.json"


def load_generated_tracking(root: Path) -> set[str]:
    """Load the set of previously generated file paths."""
    tracking_path = root / GENERATED_TRACKING_FILE
    if not tracking_path.exists():
        return set()

    try:
        data = json.loads(tracking_path.read_text(encoding="utf-8"))
        return set(data.get("files", []))
    except (json.JSONDecodeError, KeyError):
        return set()


def save_generated_tracking(root: Path, files: set[str]) -> None:
    """Save the set of generated file paths."""
    tracking_path = root / GENERATED_TRACKING_FILE
    tracking_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": 1,
        "files": sorted(files),
    }
    tracking_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_generator(
    target_name: str,
    target_config: OpenCodeTarget | CopilotTarget,
    manifest: Manifest,
    root: Path,
) -> BaseGenerator | None:
    """Get the appropriate generator for a target.

    Args:
        target_name: Name of the target (e.g., 'opencode', 'copilot-vscode')
        target_config: Target configuration from manifest
        manifest: Full manifest
        root: Project root directory

    Returns:
        Generator instance or None if no generator exists for the target kind
    """
    from agent_scaffold.generators.copilot import CopilotGenerator
    from agent_scaffold.generators.opencode import OpenCodeGenerator

    if target_config.kind.value == "opencode":
        return OpenCodeGenerator(target_name, target_config, manifest, root)
    elif target_config.kind.value == "copilot":
        return CopilotGenerator(target_name, target_config, manifest, root)

    return None
