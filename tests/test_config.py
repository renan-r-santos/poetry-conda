import os
import subprocess
from pathlib import Path
from subprocess import CompletedProcess

import pytest


@pytest.mark.usefixtures("conda_environment")
class TestConfig:
    @pytest.fixture(autouse=True)
    def env(self, conda_environment: str) -> None:
        self._conda_environment = conda_environment

    def _run_command(self, command: str, check: bool = True) -> CompletedProcess[str]:
        return subprocess.run(
            ["conda", "run", "--prefix", self._conda_environment, *command.split()],
            capture_output=True,
            check=check,
            text=True,
        )

    def test_setting_not_available_if_plugin_not_installed(self, remove_poetry_conda_plugin: None) -> None:
        result = self._run_command("poetry config virtualenvs.ignore-conda-env", check=False)
        assert result.stderr.strip().splitlines()[0] == "There is no virtualenvs.ignore-conda-env setting."

    def test_default_value(self) -> None:
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"

    def test_change_setting_using_environment_variable(self) -> None:
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"

        result = self._run_command(
            "POETRY_VIRTUALENVS_IGNORE_CONDA_ENV=false poetry config virtualenvs.ignore-conda-env"
        )
        assert result.stdout.strip() == "false"

    def test_change_setting_using_the_config_command(self) -> None:
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"

        self._run_command("poetry config virtualenvs.ignore-conda-env false")
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "false"

        self._run_command("poetry config virtualenvs.ignore-conda-env --unset")
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"

    def test_change_setting_using_the_config_file(self, test_project_dir: Path) -> None:
        poetry_config_file = test_project_dir / "poetry.toml"
        poetry_config_file.unlink(missing_ok=True)

        os.chdir(test_project_dir)

        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"

        result = self._run_command("poetry config virtualenvs.ignore-conda-env false --local")
        assert poetry_config_file.read_text().strip() == "[virtualenvs]\nignore-conda-env = false"

        poetry_config_file.unlink(missing_ok=False)
        result = self._run_command("poetry config virtualenvs.ignore-conda-env")
        assert result.stdout.strip() == "true"
