import os
import random
import subprocess
from pathlib import Path
from string import ascii_letters, digits
from typing import Iterator

import pytest


@pytest.fixture(scope="session", autouse=True)
def _use_poetry_env_var_config() -> None:
    # Triggers https://github.com/renan-r-santos/poetry-conda/issues/7
    os.environ["POETRY_VIRTUALENVS_PROMPT"] = "{project_name}-py{python_version}"


@pytest.fixture(
    scope="session",
    params=[
        {"python": "3.9", "poetry": "1.5.0"},
        {"python": "3.10", "poetry": "1.5.0"},
        {"python": "3.11", "poetry": "1.5.1"},
        {"python": "3.12", "poetry": "1.8.5"},
        {"python": "3.13", "poetry": "1.8.5"},
        {"python": "3.13", "poetry": "2.0.1"},
    ],
    ids=lambda param: f"python-{param['python']}-poetry-{param['poetry']}",
)
def pixi_environment(request: pytest.FixtureRequest) -> Iterator[str]:
    python_version = request.param.get("python")
    poetry_version = request.param.get("poetry")

    random_string = "".join(random.choices(ascii_letters + digits, k=8))
    tmp_path = f"/tmp/{random_string}-test-poetry-conda-python-{python_version}-poetry-{poetry_version}"
    Path(tmp_path).mkdir(parents=True, exist_ok=True)

    subprocess.run(["pixi", "init", tmp_path], check=True)
    subprocess.run(
        [
            "pixi",
            "add",
            "--manifest-path",
            f"{tmp_path}/pixi.toml",
            f"python={python_version}",
            f"poetry={poetry_version}",
        ],
        check=True,
    )

    root_dir = Path(__file__).parent.parent
    subprocess.run(
        ["pixi", "add", "--manifest-path", f"{tmp_path}/pixi.toml", "--pypi", f"poetry-conda@file://{root_dir}"],
        check=True,
    )

    yield tmp_path

    subprocess.run(["pixi", "remove", "--manifest-path", f"{tmp_path}/pixi.toml", "--pypi", "poetry-conda"], check=True)


@pytest.fixture
def _remove_poetry_conda_plugin(pixi_environment: str) -> Iterator[None]:
    subprocess.run(
        ["pixi", "remove", "--manifest-path", f"{pixi_environment}/pixi.toml", "--pypi", "poetry-conda"], check=True
    )

    yield

    root_dir = Path(__file__).parent.parent
    subprocess.run(
        [
            "pixi",
            "add",
            "--manifest-path",
            f"{pixi_environment}/pixi.toml",
            "--pypi",
            f"poetry-conda@file://{root_dir}",
        ],
        check=True,
    )


@pytest.fixture
def test_project_dir() -> Iterator[Path]:
    test_project_dir = Path(__file__).parent / "test_project"
    current_cwd = Path.cwd()

    os.chdir(test_project_dir)
    yield test_project_dir
    os.chdir(current_cwd)
