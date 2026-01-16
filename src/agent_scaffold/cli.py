"""CLI entry point for agent-scaffold."""

from pathlib import Path

import click

from agent_scaffold import __version__
from agent_scaffold.commands.add import (
    add_agent,
    add_command,
    add_instruction,
    add_prompt,
    add_skill,
)
from agent_scaffold.commands.doctor import doctor_cmd
from agent_scaffold.commands.init import init_cmd
from agent_scaffold.commands.sync import sync_cmd


@click.group()
@click.version_option(version=__version__, prog_name="agent-scaffold")
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
    default=".",
    help="Project root directory (default: current directory)",
)
@click.pass_context
def main(ctx: click.Context, root: Path) -> None:
    """Multi-agent scaffold for AI coding assistants.

    Maintains a single source of truth for AI assistant configurations
    under .agents/, generating target-specific files for OpenCode,
    GitHub Copilot VS Code, and GitHub Copilot CLI.

    \b
    Quick start:
      agent-scaffold init
      agent-scaffold add-agent reviewer
      agent-scaffold sync
    """
    ctx.ensure_object(dict)
    ctx.obj["root"] = root


# Register commands
main.add_command(init_cmd, name="init")
main.add_command(add_prompt, name="add-prompt")
main.add_command(add_agent, name="add-agent")
main.add_command(add_instruction, name="add-instruction")
main.add_command(add_skill, name="add-skill")
main.add_command(add_command, name="add-command")
main.add_command(sync_cmd, name="sync")
main.add_command(doctor_cmd, name="doctor")


if __name__ == "__main__":
    main()
