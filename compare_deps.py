import tomllib
from packaging.requirements import Requirement
from io import TextIOBase
from typing import Iterator, List, Union
import requests
from io import StringIO

def extract_deps_requirements(filehandle: TextIOBase) -> Iterator[str]:
    """Extract deps from requirements.txt filehandle (local/remote).
    
    Yields: "pkg==>=1.0"
    """
    for line in filehandle:
        line = line.strip()
        if line and not line.startswith('#'):
            req = Requirement(line)
            yield f"{req.name}=={req.specifier}"

def extract_deps_pyproject(filehandle: TextIOBase) -> Iterator[str]:
    """Extract deps from pyproject.toml filehandle.
    
    Yields: "pkg==>=1.0", "[group] pkg==~=2.0"
    """
    data = tomllib.load(filehandle)
    
    # [project.dependencies]
    if 'project' in data and 'dependencies' in data['project']:
        for dep in data['project']['dependencies']:
            req = Requirement(dep)
            yield f"{req.name}=={req.specifier}"
    
    # [project.optional-dependencies]
    if 'project' in data and 'optional-dependencies' in data['project']:
        for group, deps in data['project']['optional-dependencies'].items():
            for dep in deps:
                req = Requirement(dep)
                yield f"[{group}] {req.name}=={req.specifier}"
    
    # [tool.*.dependencies] (uv, poetry, etc.)
    if 'tool' in data:
        for tool, config in data['tool'].items():
            if 'dependencies' in config:
                for dep in config['dependencies']:
                    req = Requirement(dep)
                    yield f"[{tool}] {req.name}=={req.specifier}"

with open('pyproject.toml', 'rb') as f:
    local_deps = list(extract_deps_pyproject(f))

print(local_deps)

remote_req_url = 'https://raw.githubusercontent.com/Comfy-Org/ComfyUI/refs/heads/master/requirements.txt'
req_fh = StringIO(requests.get(remote_req_url).text)
remote_deps = list(extract_deps_requirements(req_fh))

print(remote_deps)
