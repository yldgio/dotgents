"""init command - Create .agents/ structure and initial manifest."""

from pathlib import Path

import click
from rich.console import Console

from agent_scaffold.manifest import create_default_manifest, find_manifest, save_manifest
from agent_scaffold.models import CopilotTargetOverride, InstructionArtifact, InstructionScope
from agent_scaffold.utils import ensure_dir

console = Console()


@click.command("init")
@click.option(
    "--name",
    "-n",
    type=str,
    default=None,
    help="Project name (defaults to directory name)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Overwrite existing manifest",
)
@click.pass_context
def init_cmd(ctx: click.Context, name: str | None, force: bool) -> None:
    """Initialize a new .agents/ directory structure.

    Creates the canonical directory structure and an initial manifest.yaml
    with default configuration for all supported targets.
    """
    root: Path = ctx.obj["root"]

    # Check if manifest already exists
    existing = find_manifest(root)
    if existing and not force:
        console.print(
            f"[red]Error:[/red] Manifest already exists at [cyan]{existing}[/cyan]"
        )
        console.print("Use [yellow]--force[/yellow] to overwrite.")
        raise SystemExit(1)

    # Determine project name
    project_name = name or root.name

    console.print(f"Initializing agent-scaffold for [cyan]{project_name}[/cyan]...")

    # Create directory structure
    agents_dir = root / ".agents"
    dirs_to_create = [
        agents_dir / "prompts",
        agents_dir / "commands",
        agents_dir / "agents",
        agents_dir / "instructions",
        agents_dir / "skills",
    ]

    for dir_path in dirs_to_create:
        ensure_dir(dir_path)
        console.print(f"  Created [dim]{dir_path.relative_to(root)}[/dim]")

    # Create default manifest
    manifest = create_default_manifest(project_name)

    # Create sample instruction file
    sample_instruction_path = agents_dir / "instructions" / "repo-default.md"
    sample_instruction_content = f"""# Repository Default Instructions

These are the default instructions for the {project_name} project.

## Guidelines

- Follow the project's coding standards
- Write clear, maintainable code
- Include appropriate documentation
- Write tests for new functionality
"""
    sample_instruction_path.write_text(sample_instruction_content, encoding="utf-8")
    console.print(
        f"  Created [dim]{sample_instruction_path.relative_to(root)}[/dim]"
    )

    # Add sample instruction to manifest
    manifest.artifacts.instructions.append(
        InstructionArtifact(
            id="repo-default",
            scope=InstructionScope.REPO,
            canonical_file=".agents/instructions/repo-default.md",
            targets={
                "copilot-vscode": CopilotTargetOverride(enabled=True),
                "copilot-cli": CopilotTargetOverride(enabled=True),
            },
        )
    )

    # Save manifest
    manifest_path = save_manifest(root, manifest)
    console.print(f"  Created [dim]{manifest_path.relative_to(root)}[/dim]")

    console.print()
    console.print("[green]Success![/green] Agent scaffold initialized.")
    console.print()
    console.print("Next steps:")
    console.print("  1. Edit [cyan].agents/instructions/repo-default.md[/cyan] with your guidelines")
    console.print("  2. Add artifacts with [yellow]agent-scaffold add-*[/yellow] commands")
    console.print("  3. Generate target files with [yellow]agent-scaffold sync[/yellow]")
