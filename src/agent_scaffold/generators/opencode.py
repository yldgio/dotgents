"""OpenCode target generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_scaffold.generators.base import BaseGenerator
from agent_scaffold.models import OpenCodeTarget, OpenCodeTargetOverride
from agent_scaffold.templates import render_template
from agent_scaffold.utils import ensure_dir


class OpenCodeGenerator(BaseGenerator):
    """Generator for OpenCode target files."""

    @property
    def config(self) -> OpenCodeTarget:
        """Get typed config."""
        return self.target_config  # type: ignore

    def list_generated_files(self) -> list[Path]:
        """List all files this generator would create."""
        files = []

        # opencode.json
        files.append(self.root / self.config.config_file)

        # AGENTS.md (if we're generating it - check if it's a "rules" project)
        # For now, we always generate it
        files.append(self.root / self.config.rules_index_file)

        return files

    def generate(self, dry_run: bool = False) -> list[Path]:
        """Generate OpenCode target files."""
        generated = []

        # Generate opencode.json
        config_path = self._generate_opencode_json(dry_run)
        if config_path:
            generated.append(config_path)

        # Generate AGENTS.md
        agents_md_path = self._generate_agents_md(dry_run)
        if agents_md_path:
            generated.append(agents_md_path)

        return generated

    def _generate_opencode_json(self, dry_run: bool) -> Path | None:
        """Generate the opencode.json configuration file."""
        config_path = self.root / self.config.config_file

        # Build the configuration object
        config: dict[str, Any] = {
            "$schema": "https://opencode.ai/config.json",
        }

        # Add instructions globs
        instructions_globs = [
            f"{self.manifest.paths.instructions_dir}/**/*.md",
        ]
        config["instructions"] = instructions_globs

        # Add commands
        for command in sorted(self.manifest.artifacts.commands, key=lambda c: c.id):
            # Check if this command is enabled for opencode
            command_targets = command.targets
            if "opencode" in command_targets:
                override = command_targets["opencode"]
                if not override.enabled:
                    continue

            # Build command config
            command_key = f"command.{command.id}"
            command_config: dict[str, Any] = {
                "description": command.description,
                "template": {"file": f"./{command.canonical_file}"},
            }

            # Add user input requirement if not default
            if command.user_input != "optional":
                command_config["userInput"] = command.user_input

            config[command_key] = command_config

        # Add agents
        for agent in sorted(self.manifest.artifacts.agents, key=lambda a: a.id):
            # Check if this agent is enabled for opencode
            agent_targets = agent.targets
            if "opencode" in agent_targets:
                agent_override = agent_targets["opencode"]
                if not agent_override.enabled:
                    continue

            # Build agent config
            agent_key = f"agent.{agent.id}"
            agent_config: dict[str, Any] = {}

            if agent.prompt_file:
                agent_config["prompt"] = {"file": f"./{agent.prompt_file}"}

            # Add overrides if present
            if "opencode" in agent_targets:
                oc_override = agent_targets["opencode"]
                if isinstance(oc_override, OpenCodeTargetOverride):
                    if oc_override.model:
                        agent_config["model"] = oc_override.model
                    if oc_override.mode:
                        agent_config["mode"] = oc_override.mode
                    if oc_override.temperature is not None:
                        agent_config["temperature"] = oc_override.temperature
                    if oc_override.steps is not None:
                        agent_config["steps"] = oc_override.steps

            if agent_config:
                config[agent_key] = agent_config

        if not dry_run:
            ensure_dir(config_path.parent)
            content = json.dumps(config, indent=2)
            config_path.write_text(content, encoding="utf-8")

        return config_path

    def _generate_agents_md(self, dry_run: bool) -> Path | None:
        """Generate the AGENTS.md rules index file."""
        agents_md_path = self.root / self.config.rules_index_file

        # Prepare data for template - filter by opencode enablement
        instructions_data = []
        for instruction in sorted(
            self.manifest.artifacts.instructions, key=lambda i: i.id
        ):
            # Check if this instruction is enabled for opencode
            if "opencode" in instruction.targets:
                override = instruction.targets["opencode"]
                if not override.enabled:
                    continue
            instructions_data.append(instruction)

        agents_data = []
        for agent in sorted(self.manifest.artifacts.agents, key=lambda a: a.id):
            # Check if this agent is enabled for opencode
            if "opencode" in agent.targets:
                override = agent.targets["opencode"]
                if not override.enabled:
                    continue
            agents_data.append(agent)

        # Render template
        content = render_template(
            "opencode/AGENTS.md.j2",
            instructions=instructions_data,
            agents=agents_data,
        )

        if not dry_run:
            ensure_dir(agents_md_path.parent)
            agents_md_path.write_text(content, encoding="utf-8")

        return agents_md_path
