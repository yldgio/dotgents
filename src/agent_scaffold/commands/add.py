"""add-* commands - Add new artifacts to the manifest."""

from pathlib import Path

import click
from rich.console import Console

from agent_scaffold.manifest import (
    ManifestNotFoundError,
    load_manifest,
    save_manifest,
)
from agent_scaffold.models import (
    AgentArtifact,
    CommandArtifact,
    CopilotTargetOverride,
    InstructionArtifact,
    InstructionScope,
    OpenCodeTargetOverride,
    PromptArtifact,
    SkillArtifact,
)
from agent_scaffold.utils import ensure_dir, is_kebab_case

console = Console()


def validate_id(artifact_id: str) -> None:
    """Validate that an artifact ID is kebab-case."""
    if not is_kebab_case(artifact_id):
        console.print(
            f"[red]Error:[/red] Invalid ID [yellow]{artifact_id}[/yellow]. "
            "IDs must be kebab-case (lowercase letters, numbers, hyphens)."
        )
        console.print("Example: [green]my-artifact-name[/green]")
        raise SystemExit(1)


def check_id_exists(manifest, artifact_type: str, artifact_id: str) -> None:
    """Check if an artifact ID already exists in the manifest."""
    artifacts = getattr(manifest.artifacts, artifact_type, [])
    for artifact in artifacts:
        if artifact.id == artifact_id:
            console.print(
                f"[red]Error:[/red] {artifact_type[:-1].title()} with ID "
                f"[yellow]{artifact_id}[/yellow] already exists."
            )
            raise SystemExit(1)


# =============================================================================
# add-prompt
# =============================================================================


@click.command("add-prompt")
@click.argument("artifact_id")
@click.option("--title", "-t", type=str, default=None, help="Human-readable title")
@click.option("--description", "-d", type=str, default=None, help="Brief description")
@click.option(
    "--agent",
    "-a",
    type=str,
    default=None,
    help="Default agent (ask, edit, etc.)",
)
@click.pass_context
def add_prompt(
    ctx: click.Context,
    artifact_id: str,
    title: str | None,
    description: str | None,
    agent: str | None,
) -> None:
    """Add a new prompt artifact.

    Creates a canonical prompt file and adds it to the manifest.
    Prompts are primarily used by Copilot VS Code.
    """
    root: Path = ctx.obj["root"]

    validate_id(artifact_id)

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    check_id_exists(manifest, "prompts", artifact_id)

    # Create canonical file
    canonical_path = root / manifest.paths.prompts_dir / f"{artifact_id}.md"
    ensure_dir(canonical_path.parent)

    prompt_title = title or artifact_id.replace("-", " ").title()
    canonical_content = f"""# {prompt_title}

<!-- Add your prompt content here -->

"""
    canonical_path.write_text(canonical_content, encoding="utf-8")
    console.print(f"Created [cyan]{canonical_path.relative_to(root)}[/cyan]")

    # Build frontmatter for Copilot target
    frontmatter: dict = {"name": artifact_id}
    if description:
        frontmatter["description"] = description
    if agent:
        frontmatter["agent"] = agent

    # Add to manifest
    artifact = PromptArtifact(
        id=artifact_id,
        title=prompt_title,
        canonical_file=str(canonical_path.relative_to(root)).replace("\\", "/"),
        description=description,
        default_agent=agent,
        targets={
            "copilot-vscode": CopilotTargetOverride(enabled=True, frontmatter=frontmatter),
        },
    )
    manifest.artifacts.prompts.append(artifact)

    # Save manifest
    save_manifest(root, manifest)
    console.print(f"Added prompt [green]{artifact_id}[/green] to manifest")
    console.print()
    console.print(f"Edit [cyan]{canonical_path.relative_to(root)}[/cyan] to add your prompt content.")
    console.print("Run [yellow]agent-scaffold sync[/yellow] to generate target files.")


# =============================================================================
# add-agent
# =============================================================================


@click.command("add-agent")
@click.argument("artifact_id")
@click.option("--description", "-d", type=str, default=None, help="Agent description")
@click.option(
    "--opencode-only",
    is_flag=True,
    default=False,
    help="Only enable for OpenCode target",
)
@click.option(
    "--copilot-only",
    is_flag=True,
    default=False,
    help="Only enable for Copilot targets",
)
@click.pass_context
def add_agent(
    ctx: click.Context,
    artifact_id: str,
    description: str | None,
    opencode_only: bool,
    copilot_only: bool,
) -> None:
    """Add a new agent artifact.

    Creates a canonical agent file and adds it to the manifest.
    Agents can be used by both OpenCode and Copilot.
    """
    root: Path = ctx.obj["root"]

    validate_id(artifact_id)

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    check_id_exists(manifest, "agents", artifact_id)

    # Create canonical file
    canonical_path = root / manifest.paths.agents_dir / f"{artifact_id}.md"
    ensure_dir(canonical_path.parent)

    agent_description = description or f"{artifact_id.replace('-', ' ').title()} agent"
    canonical_content = f"""# {artifact_id.replace('-', ' ').title()} Agent

{agent_description}

## Capabilities

<!-- Define your agent's personality and capabilities here -->

## Instructions

<!-- Add specific instructions for the agent -->

"""
    canonical_path.write_text(canonical_content, encoding="utf-8")
    console.print(f"Created [cyan]{canonical_path.relative_to(root)}[/cyan]")

    # Build targets
    targets: dict = {}
    if not copilot_only:
        targets["opencode"] = OpenCodeTargetOverride(enabled=True)
    if not opencode_only:
        frontmatter = {"name": artifact_id, "description": agent_description}
        targets["copilot-vscode"] = CopilotTargetOverride(enabled=True, frontmatter=frontmatter)
        targets["copilot-cli"] = CopilotTargetOverride(enabled=True, frontmatter=frontmatter)

    # Add to manifest
    artifact = AgentArtifact(
        id=artifact_id,
        description=agent_description,
        prompt_file=str(canonical_path.relative_to(root)).replace("\\", "/"),
        targets=targets,
    )
    manifest.artifacts.agents.append(artifact)

    # Save manifest
    save_manifest(root, manifest)
    console.print(f"Added agent [green]{artifact_id}[/green] to manifest")
    console.print()
    console.print(f"Edit [cyan]{canonical_path.relative_to(root)}[/cyan] to define your agent.")
    console.print("Run [yellow]agent-scaffold sync[/yellow] to generate target files.")


# =============================================================================
# add-instruction
# =============================================================================


@click.command("add-instruction")
@click.argument("artifact_id")
@click.option(
    "--scope",
    "-s",
    type=click.Choice(["repo", "path"]),
    required=True,
    help="Instruction scope (repo-wide or path-specific)",
)
@click.option(
    "--apply-to",
    "-a",
    type=str,
    default=None,
    help="Glob pattern for path-scoped instructions (e.g., '**/*.ts')",
)
@click.pass_context
def add_instruction(
    ctx: click.Context,
    artifact_id: str,
    scope: str,
    apply_to: str | None,
) -> None:
    """Add a new instruction artifact.

    Creates a canonical instruction file and adds it to the manifest.
    Instructions can be repo-wide or scoped to specific file paths.
    """
    root: Path = ctx.obj["root"]

    validate_id(artifact_id)

    # Validate path-scoped instructions have apply_to
    if scope == "path" and not apply_to:
        console.print(
            "[red]Error:[/red] Path-scoped instructions require [yellow]--apply-to[/yellow]"
        )
        raise SystemExit(1)

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    check_id_exists(manifest, "instructions", artifact_id)

    # Create canonical file
    canonical_path = root / manifest.paths.instructions_dir / f"{artifact_id}.md"
    ensure_dir(canonical_path.parent)

    title = artifact_id.replace("-", " ").title()
    scope_text = "repository-wide" if scope == "repo" else f"files matching `{apply_to}`"
    canonical_content = f"""# {title} Instructions

These instructions apply to {scope_text}.

## Guidelines

<!-- Add your instruction content here -->

"""
    canonical_path.write_text(canonical_content, encoding="utf-8")
    console.print(f"Created [cyan]{canonical_path.relative_to(root)}[/cyan]")

    # Build targets
    frontmatter = {}
    if apply_to:
        frontmatter["applyTo"] = apply_to

    targets = {
        "copilot-vscode": CopilotTargetOverride(enabled=True, frontmatter=frontmatter),
        "copilot-cli": CopilotTargetOverride(enabled=True, frontmatter=frontmatter),
    }

    # Add to manifest
    artifact = InstructionArtifact(
        id=artifact_id,
        scope=InstructionScope(scope),
        canonical_file=str(canonical_path.relative_to(root)).replace("\\", "/"),
        apply_to=apply_to,
        targets=targets,
    )
    manifest.artifacts.instructions.append(artifact)

    # Save manifest
    save_manifest(root, manifest)
    console.print(f"Added instruction [green]{artifact_id}[/green] to manifest")
    console.print()
    console.print(f"Edit [cyan]{canonical_path.relative_to(root)}[/cyan] to add your instructions.")
    console.print("Run [yellow]agent-scaffold sync[/yellow] to generate target files.")


# =============================================================================
# add-skill
# =============================================================================


@click.command("add-skill")
@click.argument("artifact_id")
@click.option("--name", "-n", type=str, default=None, help="Skill display name")
@click.option("--description", "-d", type=str, default=None, help="Skill description")
@click.pass_context
def add_skill(
    ctx: click.Context,
    artifact_id: str,
    name: str | None,
    description: str | None,
) -> None:
    """Add a new skill artifact.

    Creates a canonical skill directory with SKILL.md and adds it to the manifest.
    Skills are bundles that can include additional assets.
    """
    root: Path = ctx.obj["root"]

    validate_id(artifact_id)

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    check_id_exists(manifest, "skills", artifact_id)

    # Create skill directory
    skill_dir = root / manifest.paths.skills_dir / artifact_id
    ensure_dir(skill_dir)
    console.print(f"Created [cyan]{skill_dir.relative_to(root)}[/cyan]")

    # Create SKILL.md
    skill_file = skill_dir / "SKILL.md"
    skill_name = name or artifact_id.replace("-", " ").title()
    skill_description = description or f"{skill_name} skill"

    skill_content = f"""---
name: {skill_name}
description: {skill_description}
---

# {skill_name}

{skill_description}

## Usage

<!-- Describe how to use this skill -->

## Capabilities

<!-- List what this skill can do -->

"""
    skill_file.write_text(skill_content, encoding="utf-8")
    console.print(f"Created [cyan]{skill_file.relative_to(root)}[/cyan]")

    # Add to manifest
    artifact = SkillArtifact(
        id=artifact_id,
        canonical_dir=str(skill_dir.relative_to(root)).replace("\\", "/"),
        skill_file=str(skill_file.relative_to(root)).replace("\\", "/"),
        name=skill_name,
        description=skill_description,
        targets={
            "copilot-vscode": CopilotTargetOverride(enabled=True),
            "copilot-cli": CopilotTargetOverride(enabled=True),
        },
    )
    manifest.artifacts.skills.append(artifact)

    # Save manifest
    save_manifest(root, manifest)
    console.print(f"Added skill [green]{artifact_id}[/green] to manifest")
    console.print()
    console.print(f"Edit [cyan]{skill_file.relative_to(root)}[/cyan] to define your skill.")
    console.print("Run [yellow]agent-scaffold sync[/yellow] to generate target files.")


# =============================================================================
# add-command
# =============================================================================


@click.command("add-command")
@click.argument("artifact_id")
@click.option("--description", "-d", type=str, default="", help="Short description for the command")
@click.option(
    "--user-input",
    type=click.Choice(["required", "optional", "none"]),
    default="optional",
    help="Whether command requires user input",
)
@click.pass_context
def add_command(
    ctx: click.Context,
    artifact_id: str,
    description: str,
    user_input: str,
) -> None:
    """Add a new OpenCode slash command.

    Creates .agents/commands/<ID>.md and registers it in the manifest.
    After syncing, the command will be available as /<ID> in OpenCode.

    Example:
        agent-scaffold add-command test --description "Run test suite"
    """
    root: Path = ctx.obj["root"]

    validate_id(artifact_id)

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    check_id_exists(manifest, "commands", artifact_id)

    # Create canonical file
    canonical_path = root / manifest.paths.commands_dir / f"{artifact_id}.md"
    ensure_dir(canonical_path.parent)

    command_description = description or "Description of what this command does."
    canonical_content = f"""# /{artifact_id}

{command_description}

## Instructions

<!-- Add command instructions here -->
<!-- Use $INPUT to reference user input if user-input is required/optional -->

Run the appropriate action for this command.
"""
    canonical_path.write_text(canonical_content, encoding="utf-8")
    console.print(f"Created [cyan]{canonical_path.relative_to(root)}[/cyan]")

    # Add to manifest
    artifact = CommandArtifact(
        id=artifact_id,
        canonical_file=str(canonical_path.relative_to(root)).replace("\\", "/"),
        description=description,
        user_input=user_input,  # type: ignore
    )
    manifest.artifacts.commands.append(artifact)

    # Save manifest
    save_manifest(root, manifest)
    console.print(f"Added command [green]/{artifact_id}[/green] to manifest")
    console.print()
    console.print(f"Edit [cyan]{canonical_path.relative_to(root)}[/cyan] to add your command content.")
    console.print("Run [yellow]agent-scaffold sync[/yellow] to update opencode.json.")

