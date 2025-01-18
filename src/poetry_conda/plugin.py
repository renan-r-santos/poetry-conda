import os
from typing import Any, Callable

from poetry.config import config
from poetry.config.config import boolean_normalizer, boolean_validator
from poetry.console.application import Application
from poetry.console.commands import config as config_command
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.utils import env


class EnvManager(env.EnvManager):
    def get(self, reload: bool = False) -> env.Env:
        ignore_conda_env = self._poetry.config.get("virtualenvs.ignore-conda-env")
        conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")

        if ignore_conda_env is True and conda_default_env is not None:
            os.environ["CONDA_DEFAULT_ENV"] = "base"

        env = super().get(reload)

        if ignore_conda_env is True and conda_default_env is not None:
            os.environ["CONDA_DEFAULT_ENV"] = conda_default_env

        return env


class Config(config.Config):
    def __init__(self, *args: bool, **kwargs: bool) -> None:
        Config.default_config["virtualenvs"]["ignore-conda-env"] = True
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_normalizer(cls, name: str) -> Callable[[str], Any]:
        if name == "virtualenvs.ignore-conda-env":
            return boolean_normalizer
        return super()._get_normalizer(name)


class ConfigCommand(config_command.ConfigCommand):
    @property
    def unique_config_values(self) -> dict[str, tuple[Any, Any]]:
        unique_config_values = super().unique_config_values
        unique_config_values["virtualenvs.ignore-conda-env"] = (boolean_validator, boolean_normalizer)
        return unique_config_values


class PoetryCondaPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        config.Config = Config  # type: ignore
        config_command.ConfigCommand = ConfigCommand  # type: ignore
        env.EnvManager = EnvManager  # type: ignore
