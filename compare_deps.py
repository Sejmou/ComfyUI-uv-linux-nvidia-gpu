from dataclasses import dataclass
import tomllib
from packaging.requirements import Requirement
import requests
from pathlib import Path


def read_text(source: str) -> str:
    return Path(source).read_text(encoding="utf-8")


def extract_deps_requirements(string: str) -> list[Requirement]:
    """Extract deps from requirements.txt string.

    Returns: list of Requirement objects
    """
    deps: list[Requirement] = []
    for line in string.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            req = Requirement(line)
            deps.append(req)
    return deps


def extract_deps_pyproject(string: str) -> list[Requirement]:
    """Extract deps from pyproject.toml string.

    Yields: "pkg==>=1.0", "[group] pkg==~=2.0"
    """
    data = tomllib.loads(string)
    deps: list[Requirement] = []

    # [project.dependencies]
    if "project" in data and "dependencies" in data["project"]:
        for dep in data["project"]["dependencies"]:
            req = Requirement(dep)
            deps.append(req)

    # [project.optional-dependencies]
    if "project" in data and "optional-dependencies" in data["project"]:
        for group, deps in data["project"]["optional-dependencies"].items():
            for req in deps:
                deps.append(req)

    return deps


@dataclass
class UpdatedDependency:
    old: Requirement
    new: Requirement


@dataclass
class ComparisonResult:
    new: list[Requirement]
    removed: list[Requirement]
    updated: list[UpdatedDependency]


def compare_requirements(
    old_reqs_list: list[Requirement], new_reqs_list: list[Requirement]
) -> ComparisonResult:
    """Returns (added, removed, changed) lists, sorted by name."""
    new_reqs = set(new_reqs_list)
    old_reqs = set(old_reqs_list)
    old_req_names = set(old_req.name.lower() for old_req in old_reqs)
    new_req_names = set(new_req.name.lower() for new_req in new_reqs)
    added: set[Requirement] = set()
    removed: set[Requirement] = set()
    updated: list[UpdatedDependency] = []

    print("torch" in new_req_names)

    for new_req in new_reqs_list:
        if new_req not in old_reqs or new_req.name.lower() not in old_req_names:
            added.add(new_req)
            print(new_req.name, "added")
        else:
            updated.append(UpdatedDependency(old=new_req, new=new_req))
    for old_req in old_reqs:
        if old_req.name.lower() not in new_req_names:
            removed.add(old_req)

    return ComparisonResult(
        new=sorted(list(added), key=lambda r: r.name),
        removed=sorted(list(removed), key=lambda r: r.name),
        updated=sorted(updated, key=lambda r: r.old.name),
    )


if __name__ == "__main__":
    # misc tests
    with open("tmp/pyproject.toml", "r") as f:
        pyproject_deps = extract_deps_pyproject(f.read())

    remote_req_url = "https://raw.githubusercontent.com/Comfy-Org/ComfyUI/refs/heads/master/requirements.txt"
    local_req_path = "tmp/requirements.txt"
    if not Path(local_req_path).exists():
        with open(local_req_path, "w") as f:
            f.write(requests.get(remote_req_url).text)
    with open(local_req_path, "r") as f:
        req_deps = extract_deps_requirements(f.read())

    result = compare_requirements(pyproject_deps, req_deps)
    print("New:")
    print(result.new)
    print("-" * 100)
    print("Removed:")
    print(result.removed)
    print("-" * 100)
    print("Updated:")
    print(result.updated)
