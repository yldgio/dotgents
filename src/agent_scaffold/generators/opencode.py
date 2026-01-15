"""OpenCode target generator."""

import json
from pathlib import Path

from agent_scaffold.generators.base import BaseGenerator
from agent_scaffold.models import OpenCodeTarget
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

        # Prepare instructions globs
        instructions_globs = [
            f"{self.manifest.paths.instructions_dir}/**/*.md",
        ]

        # Prepare agents data for template
        agents_data = []
        for agent in sorted(self.manifest.artifacts.agents, key=lambda a: a.id):
            # Check if this agent is enabled for opencode
            agent_targets = agent.targets
            if "opencode" in agent_targets:
                override = agent_targets["opencode"]
                if hasattr(override, "enabled") and not override.enabled:
                    continue
            
            # Build agent data
            agent_data = {
                "id": agent.id,
                "prompt_file": agent.prompt_file,
                "model": None,
                "mode": None,
                "temperature": None,
                "steps": None,
            }
            
            # Add overrides if present
            if "opencode" in agent_targets:
                override = agent_targets["opencode"]
                if hasattr(override, "model") and override.model:
                    agent_data["model"] = override.model
                if hasattr(override, "mode") and override.mode:
                    agent_data["mode"] = override.mode
                if hasattr(override, "temperature") and override.temperature is not None:
                    agent_data["temperature"] = override.temperature
                if hasattr(override, "steps") and override.steps is not None:
                    agent_data["steps"] = override.steps

            # Only add if there's at least a prompt_file
            if agent_data["prompt_file"] or agent_data["model"] or agent_data["mode"] or agent_data["temperature"] is not None or agent_data["steps"] is not None:
                agents_data.append(agent_data)

        # Render template
        content = render_template(
            "opencode/opencode.json.j2",
            instructions=instructions_globs,
            agents=agents_data,
        )

        if not dry_run:
            ensure_dir(config_path.parent)
            config_path.write_text(content, encoding="utf-8")

        return config_path

    def _generate_agents_md(self, dry_run: bool) -> Path | None:
        """Generate the AGENTS.md rules index file."""
        agents_md_path = self.root / self.config.rules_index_file

        # Prepare data for template
        instructions_data = sorted(self.manifest.artifacts.instructions, key=lambda i: i.id)
        agents_data = sorted(self.manifest.artifacts.agents, key=lambda a: a.id)

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
