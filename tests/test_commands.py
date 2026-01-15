"""Tests for CLI commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from agent_scaffold.cli import main
from agent_scaffold.manifest import load_manifest


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_structure(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 0
            assert (Path(".agents/prompts")).exists()
            assert (Path(".agents/commands")).exists()
            assert (Path(".agents/agents")).exists()
            assert (Path(".agents/instructions")).exists()
            assert (Path(".agents/skills")).exists()
            assert (Path(".agents/manifest.yaml")).exists()

    def test_init_creates_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["init", "--name", "my-project"])

            assert result.exit_code == 0
            manifest = load_manifest(Path("."))
            assert manifest.project.name == "my-project"

    def test_init_creates_sample_instruction(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 0
            assert (Path(".agents/instructions/repo-default.md")).exists()

            manifest = load_manifest(Path("."))
            assert len(manifest.artifacts.instructions) == 1
            assert manifest.artifacts.instructions[0].id == "repo-default"

    def test_init_fails_if_exists(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_init_force_overwrites(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init", "--name", "first"])
            result = cli_runner.invoke(main, ["init", "--force", "--name", "second"])

            assert result.exit_code == 0
            manifest = load_manifest(Path("."))
            assert manifest.project.name == "second"


class TestAddPromptCommand:
    """Tests for the add-prompt command."""

    def test_add_prompt_creates_file(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-prompt", "explain-code"])

            assert result.exit_code == 0
            assert (Path(".agents/prompts/explain-code.md")).exists()

    def test_add_prompt_updates_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main, ["add-prompt", "explain-code", "--title", "Explain Code"]
            )

            manifest = load_manifest(Path("."))
            assert len(manifest.artifacts.prompts) == 1
            assert manifest.artifacts.prompts[0].id == "explain-code"
            assert manifest.artifacts.prompts[0].title == "Explain Code"

    def test_add_prompt_with_options(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main,
                [
                    "add-prompt",
                    "explain-code",
                    "--title",
                    "Explain Code",
                    "--description",
                    "Explains selected code",
                    "--agent",
                    "ask",
                ],
            )

            manifest = load_manifest(Path("."))
            prompt = manifest.artifacts.prompts[0]
            assert prompt.description == "Explains selected code"
            assert prompt.default_agent == "ask"

    def test_add_prompt_rejects_invalid_id(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-prompt", "InvalidId"])

            assert result.exit_code == 1
            assert "kebab-case" in result.output

    def test_add_prompt_rejects_duplicate(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-prompt", "explain-code"])
            result = cli_runner.invoke(main, ["add-prompt", "explain-code"])

            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_add_prompt_requires_init(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["add-prompt", "test"])

            assert result.exit_code == 1
            assert "No manifest found" in result.output


class TestAddAgentCommand:
    """Tests for the add-agent command."""

    def test_add_agent_creates_file(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-agent", "reviewer"])

            assert result.exit_code == 0
            assert (Path(".agents/agents/reviewer.md")).exists()

    def test_add_agent_updates_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main, ["add-agent", "reviewer", "--description", "Code review specialist"]
            )

            manifest = load_manifest(Path("."))
            assert len(manifest.artifacts.agents) == 1
            assert manifest.artifacts.agents[0].id == "reviewer"
            assert manifest.artifacts.agents[0].description == "Code review specialist"

    def test_add_agent_opencode_only(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-agent", "reviewer", "--opencode-only"])

            manifest = load_manifest(Path("."))
            agent = manifest.artifacts.agents[0]
            assert "opencode" in agent.targets
            assert "copilot-vscode" not in agent.targets

    def test_add_agent_copilot_only(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-agent", "reviewer", "--copilot-only"])

            manifest = load_manifest(Path("."))
            agent = manifest.artifacts.agents[0]
            assert "opencode" not in agent.targets
            assert "copilot-vscode" in agent.targets


class TestAddInstructionCommand:
    """Tests for the add-instruction command."""

    def test_add_instruction_repo_scope(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main, ["add-instruction", "coding-standards", "--scope", "repo"]
            )

            assert result.exit_code == 0
            assert (Path(".agents/instructions/coding-standards.md")).exists()

            manifest = load_manifest(Path("."))
            # +1 for repo-default created by init
            assert len(manifest.artifacts.instructions) == 2

    def test_add_instruction_path_scope(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main,
                [
                    "add-instruction",
                    "typescript",
                    "--scope",
                    "path",
                    "--apply-to",
                    "**/*.ts",
                ],
            )

            assert result.exit_code == 0

            manifest = load_manifest(Path("."))
            ts_instruction = next(
                i for i in manifest.artifacts.instructions if i.id == "typescript"
            )
            assert ts_instruction.apply_to == "**/*.ts"

    def test_add_instruction_path_requires_apply_to(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main, ["add-instruction", "typescript", "--scope", "path"]
            )

            assert result.exit_code == 1
            assert "--apply-to" in result.output


class TestAddSkillCommand:
    """Tests for the add-skill command."""

    def test_add_skill_creates_directory(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-skill", "api-builder"])

            assert result.exit_code == 0
            assert (Path(".agents/skills/api-builder")).is_dir()
            assert (Path(".agents/skills/api-builder/SKILL.md")).exists()

    def test_add_skill_updates_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main,
                [
                    "add-skill",
                    "api-builder",
                    "--name",
                    "API Builder",
                    "--description",
                    "Build APIs quickly",
                ],
            )

            manifest = load_manifest(Path("."))
            assert len(manifest.artifacts.skills) == 1
            skill = manifest.artifacts.skills[0]
            assert skill.id == "api-builder"
            assert skill.name == "API Builder"
            assert skill.description == "Build APIs quickly"


class TestAddCommandCommand:
    """Tests for the add-command command."""

    def test_add_command_creates_file(self, cli_runner: CliRunner, tmp_path: Path):
        """Test that add-command creates the canonical file."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-command", "test"])

            assert result.exit_code == 0
            assert (Path(".agents/commands/test.md")).exists()

    def test_add_command_updates_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        """Test that add-command updates the manifest."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "build"])

            manifest = load_manifest(Path("."))
            assert len(manifest.artifacts.commands) == 1
            assert manifest.artifacts.commands[0].id == "build"

    def test_add_command_with_description(self, cli_runner: CliRunner, tmp_path: Path):
        """Test command with description."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main, ["add-command", "build", "-d", "Run build"]
            )

            assert result.exit_code == 0
            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.id == "build"
            assert cmd.description == "Run build"

    def test_add_command_user_input_required(self, cli_runner: CliRunner, tmp_path: Path):
        """Test command with required user input."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main, ["add-command", "search", "--user-input", "required"]
            )

            assert result.exit_code == 0
            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.id == "search"
            assert cmd.user_input == "required"

    def test_add_command_user_input_none(self, cli_runner: CliRunner, tmp_path: Path):
        """Test command with no user input."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(
                main, ["add-command", "status", "--user-input", "none"]
            )

            assert result.exit_code == 0
            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.user_input == "none"

    def test_add_command_user_input_optional_default(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test command defaults to optional user input."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "test"])

            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.user_input == "optional"

    def test_add_command_rejects_invalid_id(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that add-command rejects invalid IDs."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["add-command", "InvalidId"])

            assert result.exit_code == 1
            assert "kebab-case" in result.output

    def test_add_command_rejects_duplicate(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that add-command rejects duplicate IDs."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "test"])
            result = cli_runner.invoke(main, ["add-command", "test"])

            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_add_command_requires_init(self, cli_runner: CliRunner, tmp_path: Path):
        """Test that add-command requires a manifest."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["add-command", "test"])

            assert result.exit_code == 1
            assert "No manifest found" in result.output

    def test_add_command_file_content(self, cli_runner: CliRunner, tmp_path: Path):
        """Test the content of the created command file."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main, ["add-command", "deploy", "-d", "Deploy application"]
            )

            content = Path(".agents/commands/deploy.md").read_text()
            assert "# /deploy" in content
            assert "Deploy application" in content
            assert "$INPUT" in content

    def test_add_command_canonical_file_path(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that canonical file path is correctly set."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "lint"])

            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.canonical_file == ".agents/commands/lint.md"

    def test_add_command_empty_targets(self, cli_runner: CliRunner, tmp_path: Path):
        """Test that command targets default to empty dict."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "test"])

            manifest = load_manifest(Path("."))
            cmd = manifest.artifacts.commands[0]
            assert cmd.targets == {}


class TestSyncCommand:
    """Tests for the sync command."""

    def test_sync_requires_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["sync"])

            assert result.exit_code == 1
            assert "No manifest found" in result.output

    def test_sync_generates_files(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-agent", "reviewer"])
            result = cli_runner.invoke(main, ["sync"])

            assert result.exit_code == 0
            assert "Generated" in result.output

    def test_sync_dry_run(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-agent", "reviewer"])
            result = cli_runner.invoke(main, ["sync", "--dry-run"])

            assert result.exit_code == 0
            assert "Dry run" in result.output
            assert "Would create" in result.output
            # Files should not actually be created
            assert not (Path(".github/agents/reviewer.agent.md")).exists()

    def test_sync_specific_target(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-agent", "reviewer"])
            result = cli_runner.invoke(main, ["sync", "--target", "opencode"])

            assert result.exit_code == 0
            assert (Path("opencode.json")).exists()
            # Copilot files should not be created
            assert not (Path(".github/agents")).exists()

    def test_sync_unknown_target_fails(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["sync", "--target", "unknown"])

            assert result.exit_code == 1
            assert "Unknown target" in result.output

    def test_sync_generates_command_in_opencode_json(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that sync includes commands in opencode.json."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main, ["add-command", "test", "-d", "Run tests"]
            )
            result = cli_runner.invoke(main, ["sync", "--target", "opencode"])

            assert result.exit_code == 0
            assert (Path("opencode.json")).exists()

            import json
            config = json.loads(Path("opencode.json").read_text())
            assert "command.test" in config
            assert config["command.test"]["description"] == "Run tests"
            assert config["command.test"]["template"]["file"] == "./.agents/commands/test.md"

    def test_sync_generates_command_with_user_input(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that sync includes userInput in opencode.json when not optional."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(
                main,
                [
                    "add-command",
                    "search",
                    "-d",
                    "Search code",
                    "--user-input",
                    "required",
                ],
            )
            result = cli_runner.invoke(main, ["sync", "--target", "opencode"])

            assert result.exit_code == 0

            import json
            config = json.loads(Path("opencode.json").read_text())
            assert "command.search" in config
            assert config["command.search"]["userInput"] == "required"

    def test_sync_omits_user_input_when_optional(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that sync omits userInput from opencode.json when optional (default)."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "build"])
            result = cli_runner.invoke(main, ["sync", "--target", "opencode"])

            assert result.exit_code == 0

            import json
            config = json.loads(Path("opencode.json").read_text())
            assert "command.build" in config
            assert "userInput" not in config["command.build"]

    def test_sync_multiple_commands_sorted(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that sync generates multiple commands in sorted order."""
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            cli_runner.invoke(main, ["add-command", "zebra"])
            cli_runner.invoke(main, ["add-command", "alpha"])
            cli_runner.invoke(main, ["add-command", "beta"])
            result = cli_runner.invoke(main, ["sync", "--target", "opencode"])

            assert result.exit_code == 0

            import json
            config = json.loads(Path("opencode.json").read_text())
            command_keys = [k for k in config.keys() if k.startswith("command.")]
            # Commands should be sorted alphabetically
            assert command_keys == ["command.alpha", "command.beta", "command.zebra"]


class TestDoctorCommand:
    """Tests for the doctor command."""

    def test_doctor_requires_manifest(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["doctor"])

            assert result.exit_code == 1
            assert "FAIL" in result.output

    def test_doctor_passes_on_valid_setup(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            result = cli_runner.invoke(main, ["doctor"])

            assert result.exit_code == 0
            assert "passed" in result.output

    def test_doctor_detects_missing_file(self, cli_runner: CliRunner, tmp_path: Path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            cli_runner.invoke(main, ["init"])
            # Delete the repo-default instruction file
            (Path(".agents/instructions/repo-default.md")).unlink()
            result = cli_runner.invoke(main, ["doctor"])

            assert result.exit_code == 1
            assert "FAIL" in result.output
            assert "Canonical files exist" in result.output


class TestRootOption:
    """Tests for the --root option."""

    def test_root_option_init(self, cli_runner: CliRunner, tmp_path: Path):
        target_dir = tmp_path / "subproject"
        target_dir.mkdir()

        result = cli_runner.invoke(main, ["--root", str(target_dir), "init"])

        assert result.exit_code == 0
        assert (target_dir / ".agents" / "manifest.yaml").exists()

    def test_root_option_sync(self, cli_runner: CliRunner, tmp_path: Path):
        target_dir = tmp_path / "subproject"
        target_dir.mkdir()

        cli_runner.invoke(main, ["--root", str(target_dir), "init"])
        cli_runner.invoke(main, ["--root", str(target_dir), "add-agent", "test-agent"])
        result = cli_runner.invoke(main, ["--root", str(target_dir), "sync"])

        assert result.exit_code == 0
        assert (target_dir / "opencode.json").exists()
