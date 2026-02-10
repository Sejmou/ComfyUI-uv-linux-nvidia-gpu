import requests

response = requests.get(
    "https://api.github.com/repos/Comfy-Org/ComfyUI/releases",
    headers={"Accept": "application/vnd.github+json"},
)
releases = response.json()
for release in releases:
    print(release["tag_name"], release["published_at"])
