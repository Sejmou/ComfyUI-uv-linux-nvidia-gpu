import tomllib
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
        prompt="Enter the path to the folder to install ComfyUI in (will be created if it doesn't exist)",
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
        clone_repo()

    update()


def clone_repo():
    typer.echo(f"Cloning repo {REPO_URL}")
    subprocess.run(["git", "clone", REPO_URL, "."])


def update():
    typer.echo(f"Creating or updating pyproject.toml for uv")
    # extract version from current pyproject.toml
    toml_path = Path(os.getcwd(), "pyproject.toml")

    data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    version = data["project"]["version"]

    typer.echo(f"Current version: {version}")
    # remove the repo's pyproject.toml; conflicts with pyproject.toml used by uv!
    toml_path.unlink()

    subprocess.run(["uv", "init", "--python", "3.13"])

    subprocess.run(["uv", "add", "-r", "requirements.txt"])

    install_manager = typer.confirm(
        "Should ComfyUI manager be installed too? - more details: https://github.com/Comfy-Org/ComfyUI-Manager/tree/manager-v4",
        default=True,
    )
    if install_manager:
        subprocess.run(["uv", "add", "-r", "manager_requirements.txt"])

    # add the CUDA GPU config to pyproject.toml
    cuda_gpu_config = """[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
[tool.uv.sources]
torch = [
  { index = "pytorch-cu130", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchvision = [
  { index = "pytorch-cu130", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchaudio = [
  { index = "pytorch-cu130", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]"""
    with open("pyproject.toml", "a") as f:
        f.write(cuda_gpu_config)

    # run uv sync to install the dependencies (this time from proper package index)
    subprocess.run(["uv", "sync"])


if __name__ == "__main__":
    app()
