"""doctor command - Validate manifest and file integrity."""

from pathlib import Path

import click
from rich.console import Console

from agent_scaffold.manifest import (
    ManifestNotFoundError,
    ManifestValidationError,
    find_manifest,
    load_manifest,
)
from agent_scaffold.utils import is_kebab_case

# Use force_terminal=True and legacy_windows=False for proper Unicode on Windows
console = Console(force_terminal=True)


class DoctorCheck:
    """Result of a single doctor check."""

    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message


def check_manifest_exists(root: Path) -> DoctorCheck:
    """Check if manifest file exists."""
    manifest_path = find_manifest(root)
    if manifest_path:
        return DoctorCheck(
            "Manifest exists", True, str(manifest_path.relative_to(root))
        )
    return DoctorCheck("Manifest exists", False, "No manifest found")


def check_manifest_valid(root: Path) -> DoctorCheck:
    """Check if manifest is valid."""
    try:
        load_manifest(root)
        return DoctorCheck("Manifest valid", True)
    except ManifestNotFoundError:
        return DoctorCheck("Manifest valid", False, "Manifest not found")
    except ManifestValidationError as e:
        return DoctorCheck("Manifest valid", False, str(e))


def check_canonical_files_exist(root: Path) -> DoctorCheck:
    """Check if all referenced canonical files exist."""
    try:
        manifest = load_manifest(root)
    except (ManifestNotFoundError, ManifestValidationError):
        return DoctorCheck("Canonical files exist", False, "Cannot load manifest")

    missing = []

    # Check prompts
    for prompt in manifest.artifacts.prompts:
        path = root / prompt.canonical_file
        if not path.exists():
            missing.append(prompt.canonical_file)

    # Check agents
    for agent in manifest.artifacts.agents:
        if agent.prompt_file:
            path = root / agent.prompt_file
            if not path.exists():
                missing.append(agent.prompt_file)

    # Check instructions
    for instruction in manifest.artifacts.instructions:
        path = root / instruction.canonical_file
        if not path.exists():
            missing.append(instruction.canonical_file)

    # Check skills
    for skill in manifest.artifacts.skills:
        path = root / skill.skill_file
        if not path.exists():
            missing.append(skill.skill_file)

    if missing:
        return DoctorCheck(
            "Canonical files exist",
            False,
            f"Missing files: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}",
        )
    return DoctorCheck("Canonical files exist", True)


def check_ids_unique(root: Path) -> DoctorCheck:
    """Check if all artifact IDs are unique within their type."""
    try:
        manifest = load_manifest(root)
    except (ManifestNotFoundError, ManifestValidationError):
        return DoctorCheck("IDs unique", False, "Cannot load manifest")

    duplicates = []

    for artifact_type in ["prompts", "agents", "instructions", "skills"]:
        artifacts = getattr(manifest.artifacts, artifact_type, [])
        ids = [a.id for a in artifacts]
        seen = set()
        for id_ in ids:
            if id_ in seen:
                duplicates.append(f"{artifact_type}.{id_}")
            seen.add(id_)

    if duplicates:
        return DoctorCheck("IDs unique", False, f"Duplicates: {', '.join(duplicates)}")
    return DoctorCheck("IDs unique", True)


def check_ids_kebab_case(root: Path) -> DoctorCheck:
    """Check if all artifact IDs follow kebab-case convention."""
    try:
        manifest = load_manifest(root)
    except (ManifestNotFoundError, ManifestValidationError):
        return DoctorCheck("IDs kebab-case", False, "Cannot load manifest")

    invalid = []

    for artifact_type in ["prompts", "agents", "instructions", "skills"]:
        artifacts = getattr(manifest.artifacts, artifact_type, [])
        for artifact in artifacts:
            if not is_kebab_case(artifact.id):
                invalid.append(artifact.id)

    if invalid:
        return DoctorCheck(
            "IDs kebab-case", False, f"Invalid IDs: {', '.join(invalid)}"
        )
    return DoctorCheck("IDs kebab-case", True)


def check_path_instructions_have_apply_to(root: Path) -> DoctorCheck:
    """Check if path-scoped instructions have applyTo defined."""
    try:
        manifest = load_manifest(root)
    except (ManifestNotFoundError, ManifestValidationError):
        return DoctorCheck("Path instructions valid", False, "Cannot load manifest")

    missing_apply_to = []

    for instruction in manifest.artifacts.instructions:
        if instruction.scope.value == "path" and not instruction.apply_to:
            missing_apply_to.append(instruction.id)

    if missing_apply_to:
        return DoctorCheck(
            "Path instructions valid",
            False,
            f"Missing applyTo: {', '.join(missing_apply_to)}",
        )
    return DoctorCheck("Path instructions valid", True)


@click.command("doctor")
@click.pass_context
def doctor_cmd(ctx: click.Context) -> None:
    """Validate manifest and check file integrity.

    Runs a series of checks to ensure the manifest is valid,
    all referenced files exist, and naming conventions are followed.
    """
    root: Path = ctx.obj["root"]

    console.print("Running doctor checks...\n")

    checks = [
        check_manifest_exists(root),
        check_manifest_valid(root),
        check_canonical_files_exist(root),
        check_ids_unique(root),
        check_ids_kebab_case(root),
        check_path_instructions_have_apply_to(root),
    ]

    passed = 0
    failed = 0

    for check in checks:
        if check.passed:
            status = "[green]PASS[/green]"
            passed += 1
        else:
            status = "[red]FAIL[/red]"
            failed += 1

        message = f" - {check.message}" if check.message else ""
        console.print(f"{status} {check.name}{message}")

    console.print()
    if failed == 0:
        console.print(f"[green]All {passed} checks passed![/green]")
    else:
        console.print(f"[yellow]{passed} passed, {failed} failed[/yellow]")
        raise SystemExit(1)
