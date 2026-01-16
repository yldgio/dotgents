"""sync command - Generate target files from manifest."""

from pathlib import Path

import click
from rich.console import Console

from agent_scaffold.generators import get_generator
from agent_scaffold.manifest import ManifestNotFoundError, load_manifest

console = Console()


@click.command("sync")
@click.option(
    "--prune",
    is_flag=True,
    default=False,
    help="Remove generated files no longer in manifest",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be generated without writing",
)
@click.option(
    "--target",
    "-t",
    type=str,
    default=None,
    help="Only sync a specific target",
)
@click.pass_context
def sync_cmd(
    ctx: click.Context,
    prune: bool,
    dry_run: bool,
    target: str | None,
) -> None:
    """Generate target files from the manifest.

    Reads the manifest and generates all configured target files.
    This operation is idempotent - running it multiple times
    produces identical output.
    """
    root: Path = ctx.obj["root"]

    try:
        manifest = load_manifest(root)
    except ManifestNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1) from None

    if dry_run:
        console.print("[yellow]Dry run mode - no files will be written[/yellow]")
        console.print()

    # Determine which targets to sync
    targets_to_sync = []
    if target:
        if target not in manifest.targets:
            console.print(f"[red]Error:[/red] Unknown target [yellow]{target}[/yellow]")
            console.print(f"Available targets: {', '.join(manifest.targets.keys())}")
            raise SystemExit(1)
        targets_to_sync = [target]
    else:
        targets_to_sync = [t for t, cfg in manifest.targets.items() if cfg.enabled]

    all_generated: list[Path] = []

    # Process each target
    for target_name in targets_to_sync:
        target_config = manifest.targets[target_name]
        console.print(f"Syncing [cyan]{target_name}[/cyan]...")

        generator = get_generator(target_name, target_config, manifest, root)
        if generator is None:
            console.print(
                f"  [yellow]No generator for target kind: {target_config.kind}[/yellow]"
            )
            continue

        generated = generator.generate(dry_run=dry_run)
        all_generated.extend(generated)

        for path in generated:
            rel_path = path.relative_to(root) if path.is_absolute() else path
            action = "Would create" if dry_run else "Created"
            console.print(f"  {action} [dim]{rel_path}[/dim]")

    # Convert generated paths to relative strings for tracking
    current = {str(p.relative_to(root)).replace("\\", "/") for p in all_generated}

    # Handle pruning - remove files that were previously generated but no longer needed
    if prune:
        from agent_scaffold.generators import load_generated_tracking

        previous = load_generated_tracking(root)
        stale = previous - current

        if stale:
            console.print()
            console.print("Pruning stale files...")
            for stale_path in sorted(stale):
                full_path = root / stale_path
                if full_path.exists():
                    if dry_run:
                        console.print(f"  Would remove [dim]{stale_path}[/dim]")
                    else:
                        full_path.unlink()
                        console.print(f"  Removed [dim]{stale_path}[/dim]")
                        # Also remove empty parent directories
                        _cleanup_empty_dirs(full_path.parent, root)

    # Always save tracking file (unless dry-run)
    if not dry_run:
        from agent_scaffold.generators import save_generated_tracking

        save_generated_tracking(root, current)

    # Summary
    console.print()
    if dry_run:
        console.print(f"[yellow]Would generate {len(all_generated)} files[/yellow]")
    else:
        console.print(f"[green]Generated {len(all_generated)} files[/green]")


def _cleanup_empty_dirs(directory: Path, root: Path) -> None:
    """Remove empty directories up to but not including root."""
    try:
        while directory != root and directory.is_dir():
            if any(directory.iterdir()):
                break  # Directory not empty
            directory.rmdir()
            directory = directory.parent
    except OSError:
        pass  # Ignore errors during cleanup
