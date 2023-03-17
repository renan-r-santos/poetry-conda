import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from poetry.__version__ import __version__
from poetry.config import config
from poetry.config.config import boolean_normalizer, boolean_validator
from poetry.console.application import Application
from poetry.console.commands import config as config_command
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.utils import env


class EnvManager(env.EnvManager):
    def get(self, reload: bool = False) -> env.Env:
        ignore_conda_envs = self._poetry.config.get("virtualenvs.ignore-conda-envs")
        conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")

        if ignore_conda_envs is True and conda_default_env is not None:
            os.environ["CONDA_DEFAULT_ENV"] = "base"

        env = super().get(reload)

        if ignore_conda_envs is True and conda_default_env is not None:
            os.environ["CONDA_DEFAULT_ENV"] = conda_default_env

        return env


class Config(config.Config):
    def __init__(self, use_environment: bool = True, base_dir: Optional[Path] = None) -> None:
        Config.default_config["virtualenvs"]["ignore-conda-envs"] = True
        super().__init__(use_environment, base_dir)

    @staticmethod
    def _get_normalizer(name: str) -> Callable[[str], Any]:
        if name == "virtualenvs.ignore-conda-envs":
            return boolean_normalizer
        return config.Config._get_normalizer(name)


class ConfigCommand(config_command.ConfigCommand):
    @property
    def unique_config_values(self) -> Dict[str, Tuple[Any, Any]]:
        unique_config_values = super().unique_config_values

        major, minor, _ = [int(v) for v in __version__.split(".")]
        if major == 1 and minor < 4:
            unique_config_values["virtualenvs.ignore-conda-envs"] = (boolean_validator, boolean_normalizer, True)  # type: ignore
        else:
            unique_config_values["virtualenvs.ignore-conda-envs"] = (boolean_validator, boolean_normalizer)
        return unique_config_values


class PoetryCondaPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        setattr(config, "Config", Config)
        setattr(config_command, "ConfigCommand", ConfigCommand)
        setattr(env, "EnvManager", EnvManager)
