import shutil
import subprocess
from pathlib import Path
from subprocess import CompletedProcess

import pytest


@pytest.mark.usefixtures("conda_environment")
class TestEnv:
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

    def test_poetry_ignores_conda_env(self, test_project_dir: Path) -> None:
        self._run_command("poetry config virtualenvs.in-project true --local")
        self._run_command("poetry config virtualenvs.ignore-conda-envs true --local")
        self._run_command("poetry show", check=False)

        result = self._run_command("poetry run which python")
        assert result.stdout.strip() == str(test_project_dir / ".venv" / "bin" / "python")

        (test_project_dir / "poetry.toml").unlink(missing_ok=False)
        shutil.rmtree(test_project_dir / ".venv")
        assert (test_project_dir / ".venv").exists() is False

    def test_poetry_uses_conda_env(self, test_project_dir: Path) -> None:
        self._run_command("poetry config virtualenvs.in-project true --local")
        self._run_command("poetry config virtualenvs.ignore-conda-envs false --local")
        self._run_command("poetry show", check=False)

        (test_project_dir / "poetry.toml").unlink(missing_ok=False)
        assert (test_project_dir / ".venv").exists() is False
