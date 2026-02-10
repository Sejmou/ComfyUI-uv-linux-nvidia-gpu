# [WIP] Installation Workflow for ComfyUI with uv on Linux with NVIDIA GPU
In this repo, I try to make ComfyUI installable in a more pleasant way for people running Linux with NVIDIA GPUs (things _should_ work for people on Mac as well, but without GPU support, obviously).

Things were ONLY tested on my local setup (Ubuntu 22.04, NVIDIA RTX 3090 with 24GB of VRAM).

I adapted things from the official instructions from the [README as of 2025-02-10](https://github.com/Comfy-Org/ComfyUI/blob/c1b63a7e78b606bc14cd49a02e9338274db28a60/README.md#manual-install-windows-linux) (c.f. 'Manual Install (Windows, Linux)' + subsection for NVIDIA).

I 'imported' the dependencies from the `requirements.txt` in the repo ([link](https://github.com/Comfy-Org/ComfyUI/blob/c1b63a7e78b606bc14cd49a02e9338274db28a60/requirements.txt)) by temporarily copying the file to this directory and running `uv add -r requirements.txt`. This added the dependencies into `pyproject.toml`.

Afterwards, I made sure the `torch`, `torchvision` and `torchaudio` dependencies use the correct index URL for the CUDA 13.0 builds (as mentioned in the 'NVIDIA' subsection of the 'Manual Install' section in the README) by following the [PyTorch index instructions from the `uv` docs](https://docs.astral.sh/uv/guides/integration/pytorch/#using-a-pytorch-index).

