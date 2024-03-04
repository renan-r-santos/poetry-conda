import os
import random
import subprocess
from pathlib import Path
from string import ascii_letters, digits
from typing import Iterator

import pytest
from pytest import FixtureRequest


@pytest.fixture(
    scope="session",
    params=[
        {"python": "3.8", "poetry": "1.3.0"},
        {"python": "3.9", "poetry": "1.3.0"},
        {"python": "3.10", "poetry": "1.3.0"},
        {"python": "3.11", "poetry": "1.3.0"},
        {"python": "3.11", "poetry": "1.4.0"},
        {"python": "3.11", "poetry": "1.5.1"},
        {"python": "3.12", "poetry": "1.6.1"},
        {"python": "3.12", "poetry": "1.7.1"},
        {"python": "3.12", "poetry": "1.8.2"},
    ],
    ids=lambda param: f"python-{param['python']}-poetry-{param['poetry']}",
)
def conda_environment(request: FixtureRequest) -> Iterator[str]:
    python_version = request.param.get("python")
    poetry_version = request.param.get("poetry")
    random_string = "".join(random.choices(ascii_letters + digits, k=8))
    environment_path = f"/tmp/{random_string}-test-poetry-conda-python-{python_version}-poetry-{poetry_version}"

    subprocess.run(
        [
            "conda",
            "create",
            "--prefix",
            environment_path,
            "--channel",
            "conda-forge",
            "--quiet",
            "--yes",
            f"python={python_version}",
            f"poetry={poetry_version}",
        ],
        check=True,
    )

    root_dir = Path(__file__).parent.parent
    subprocess.run(["conda", "run", "--prefix", environment_path, "pip", "install", "--no-deps", root_dir], check=True)

    yield environment_path

    subprocess.run(["conda", "remove", "--prefix", environment_path, "--all", "--quiet", "--yes"], check=True)


@pytest.fixture
def remove_poetry_conda_plugin(conda_environment: str) -> Iterator[None]:
    subprocess.run(
        ["conda", "run", "--prefix", conda_environment, "pip", "uninstall", "poetry-conda", "--yes"], check=True
    )

    yield

    root_dir = Path(__file__).parent.parent
    subprocess.run(["conda", "run", "--prefix", conda_environment, "pip", "install", "--no-deps", root_dir], check=True)


@pytest.fixture
def test_project_dir() -> Iterator[Path]:
    test_project_dir = Path(__file__).parent / "test_project"
    current_cwd = Path.cwd()

    os.chdir(test_project_dir)
    yield test_project_dir
    os.chdir(current_cwd)
