import typer
from pathlib import Path
from typing import Optional
import os
import subprocess

REPO_URL = "https://github.com/Comfy-Org/ComfyUI.git"

app = typer.Typer(add_completion=True)  # Enable shell completion


@app.command()
def main(
    folder: Path = typer.Option(
        Path("~", "comfyui").expanduser(),  # ~/comfyui default
        "--folder",
        "-f",
        prompt=True,  # ALWAYS prompt (editable default)
        dir_okay=True,
        file_okay=False,
        exists=False,
        show_default="~/comfyui",
    )
):
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    else:
        typer.echo(f"Folder {folder} already exists")

    os.chdir(folder)
    typer.echo(f"Working in {folder}")

    # check if git repo exists
    if not (folder / ".git").exists():
        clone_repo(folder)
    else:
        # get latest commit hash and date
        commit_hash = (
            subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )
        commit_date = (
            subprocess.run(["git", "log", "-1", "--format=%ad"], capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )
        typer.echo(f"Latest commit: {commit_hash} on {commit_date}")
        # ask user if they want to pull latest changes
        if typer.confirm("Do you want to pull latest changes?"):
            pull_latest(folder)

    create_or_update_pyproject(folder)


def clone_repo(folder: Path):
    typer.echo(f"Cloning repo {REPO_URL}")
    subprocess.run(["git", "clone", REPO_URL])


def pull_latest(folder: Path):
    typer.echo(f"Pulling latest changes from {REPO_URL}")
    subprocess.run(["git", "pull", REPO_URL])


def create_or_update_pyproject(folder: Path):
    typer.echo(f"Creating or updating pyproject.toml for uv")
    subprocess.run(["uv", "add", "-r", "requirements.txt"])


if __name__ == "__main__":
    app()
