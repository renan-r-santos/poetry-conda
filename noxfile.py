from nox import options, parametrize
from nox_poetry import Session, session

options.sessions = ["lint", "mypy"]


@session(venv_backend="none")
@parametrize("command", [["ruff", "check", "."], ["ruff", "format", "--check", "."]])
def lint(s: Session, command: list[str]):
    s.run(*command)


@session(venv_backend="none")
def format(s: Session) -> None:
    s.run("ruff", "check", ".", "--select", "I", "--fix")
    s.run("ruff", "format", ".")


@session(venv_backend="none")
def mypy(s: Session) -> None:
    s.run("mypy")
