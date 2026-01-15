"""Copilot target generator (VS Code and CLI)."""

from pathlib import Path

from agent_scaffold.generators.base import BaseGenerator
from agent_scaffold.models import CopilotTarget, InstructionScope
from agent_scaffold.templates import render_template
from agent_scaffold.utils import ensure_dir


class CopilotGenerator(BaseGenerator):
    """Generator for Copilot target files (VS Code and CLI)."""

    @property
    def config(self) -> CopilotTarget:
        """Get typed config."""
        return self.target_config  # type: ignore

    @property
    def is_vscode(self) -> bool:
        """Check if this is the VS Code target (has prompts)."""
        return self.config.prompts_dir is not None

    def list_generated_files(self) -> list[Path]:
        """List all files this generator would create."""
        files = []

        # Prompts (VS Code only)
        if self.is_vscode and self.config.prompts_dir:
            for prompt in self.manifest.artifacts.prompts:
                if self._is_enabled_for_target(prompt.targets):
                    files.append(self.root / self.config.prompts_dir / f"{prompt.id}.prompt.md")

        # Agents
        for agent in self.manifest.artifacts.agents:
            if self._is_enabled_for_target(agent.targets):
                files.append(self.root / self.config.agents_dir / f"{agent.id}.agent.md")

        # Instructions
        for instruction in self.manifest.artifacts.instructions:
            if self._is_enabled_for_target(instruction.targets):
                if instruction.scope == InstructionScope.REPO:
                    # Repo-wide instructions go to copilot-instructions.md
                    pass  # Handled separately
                else:
                    # Path-scoped instructions
                    files.append(
                        self.root / self.config.instructions_dir / f"{instruction.id}.instructions.md"
                    )

        # Repo instructions file
        repo_instructions = [i for i in self.manifest.artifacts.instructions if i.scope == InstructionScope.REPO]
        if repo_instructions:
            files.append(self.root / self.config.repo_instructions_file)

        # Skills
        for skill in self.manifest.artifacts.skills:
            if self._is_enabled_for_target(skill.targets):
                files.append(self.root / self.config.skills_dir / skill.id / "SKILL.md")

        return files

    def _is_enabled_for_target(self, targets: dict) -> bool:
        """Check if an artifact is enabled for this target."""
        if self.target_name not in targets:
            return True  # Default to enabled if not specified
        override = targets[self.target_name]
        if hasattr(override, "enabled"):
            return override.enabled
        return True

    def _get_frontmatter(self, targets: dict) -> dict:
        """Get frontmatter overrides for this target."""
        if self.target_name not in targets:
            return {}
        override = targets[self.target_name]
        if hasattr(override, "frontmatter"):
            return override.frontmatter
        return {}

    def generate(self, dry_run: bool = False) -> list[Path]:
        """Generate Copilot target files."""
        generated = []

        # Generate prompts (VS Code only)
        if self.is_vscode:
            generated.extend(self._generate_prompts(dry_run))

        # Generate agents
        generated.extend(self._generate_agents(dry_run))

        # Generate instructions
        generated.extend(self._generate_instructions(dry_run))

        # Generate skills
        generated.extend(self._generate_skills(dry_run))

        return generated

    def _generate_prompts(self, dry_run: bool) -> list[Path]:
        """Generate prompt files."""
        generated = []

        if not self.config.prompts_dir:
            return generated

        prompts_dir = self.root / self.config.prompts_dir

        for prompt in sorted(self.manifest.artifacts.prompts, key=lambda p: p.id):
            if not self._is_enabled_for_target(prompt.targets):
                continue

            prompt_path = prompts_dir / f"{prompt.id}.prompt.md"

            # Build frontmatter
            frontmatter = {"name": prompt.id}
            if prompt.description:
                frontmatter["description"] = prompt.description
            if prompt.default_agent:
                frontmatter["agent"] = prompt.default_agent
            if prompt.default_model:
                frontmatter["model"] = prompt.default_model
            if prompt.tools:
                frontmatter["tools"] = prompt.tools

            # Merge with target-specific frontmatter
            frontmatter.update(self._get_frontmatter(prompt.targets))

            # Render template
            content = render_template(
                "copilot/prompt.md.j2",
                frontmatter=frontmatter,
                canonical_file=prompt.canonical_file,
                id=prompt.id,
            )

            if not dry_run:
                ensure_dir(prompt_path.parent)
                prompt_path.write_text(content, encoding="utf-8")

            generated.append(prompt_path)

        return generated

    def _generate_agents(self, dry_run: bool) -> list[Path]:
        """Generate agent files."""
        generated = []

        agents_dir = self.root / self.config.agents_dir

        for agent in sorted(self.manifest.artifacts.agents, key=lambda a: a.id):
            if not self._is_enabled_for_target(agent.targets):
                continue

            agent_path = agents_dir / f"{agent.id}.agent.md"

            # Build frontmatter
            frontmatter = {
                "name": agent.id,
                "description": agent.description,
            }

            # Merge with target-specific frontmatter
            frontmatter.update(self._get_frontmatter(agent.targets))

            # Render template
            content = render_template(
                "copilot/agent.md.j2",
                frontmatter=frontmatter,
                id=agent.id,
                prompt_file=agent.prompt_file,
                prompt=agent.prompt,
            )

            if not dry_run:
                ensure_dir(agent_path.parent)
                agent_path.write_text(content, encoding="utf-8")

            generated.append(agent_path)

        return generated

    def _generate_instructions(self, dry_run: bool) -> list[Path]:
        """Generate instruction files."""
        generated = []

        instructions_dir = self.root / self.config.instructions_dir
        repo_instructions_path = self.root / self.config.repo_instructions_file

        repo_instruction_refs = []

        for instruction in sorted(self.manifest.artifacts.instructions, key=lambda i: i.id):
            if not self._is_enabled_for_target(instruction.targets):
                continue

            if instruction.scope == InstructionScope.REPO:
                # Collect repo-wide instructions for the main file
                repo_instruction_refs.append(instruction)
            else:
                # Path-scoped instruction
                instruction_path = instructions_dir / f"{instruction.id}.instructions.md"

                # Build frontmatter
                frontmatter = {}
                if instruction.apply_to:
                    frontmatter["applyTo"] = f'"{instruction.apply_to}"'

                # Merge with target-specific frontmatter
                frontmatter.update(self._get_frontmatter(instruction.targets))

                # Render template
                content = render_template(
                    "copilot/instruction.md.j2",
                    frontmatter=frontmatter,
                    id=instruction.id,
                    canonical_file=instruction.canonical_file,
                )

                if not dry_run:
                    ensure_dir(instruction_path.parent)
                    instruction_path.write_text(content, encoding="utf-8")

                generated.append(instruction_path)

        # Generate repo-wide instructions file
        if repo_instruction_refs:
            # Render template
            content = render_template(
                "copilot/copilot-instructions.md.j2",
                instructions=repo_instruction_refs,
            )

            if not dry_run:
                ensure_dir(repo_instructions_path.parent)
                repo_instructions_path.write_text(content, encoding="utf-8")

            generated.append(repo_instructions_path)

        return generated

    def _generate_skills(self, dry_run: bool) -> list[Path]:
        """Generate skill files."""
        generated = []

        skills_dir = self.root / self.config.skills_dir

        for skill in sorted(self.manifest.artifacts.skills, key=lambda s: s.id):
            if not self._is_enabled_for_target(skill.targets):
                continue

            skill_path = skills_dir / skill.id / "SKILL.md"

            # Build frontmatter
            frontmatter = {
                "name": skill.name or skill.id,
                "description": skill.description or f"{skill.id} skill",
            }

            # Render template
            content = render_template(
                "copilot/skill.md.j2",
                frontmatter=frontmatter,
                id=skill.id,
                skill_file=skill.skill_file,
            )

            if not dry_run:
                ensure_dir(skill_path.parent)
                skill_path.write_text(content, encoding="utf-8")

            generated.append(skill_path)

        return generated
