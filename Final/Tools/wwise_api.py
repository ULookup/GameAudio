"""Small local WAAPI HTTP client for the open Wwise project."""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def require_final_project():
    expected = Path(__file__).resolve().parents[1] / "Final.wproj"
    projects = call("ak.wwise.core.object.get", {"waql": "$ from type Project"},
                    {"return": ["filePath"]})["return"]
    if len(projects) != 1 or Path(projects[0]["filePath"]).resolve() != expected:
        raise RuntimeError("Open this folder's Final.wproj before using this authoring script.")


def call(uri, args=None, options=None):
    payload = json.dumps({"uri": uri, "args": args or {}, "options": options or {}}).encode("utf-8")
    request = urllib.request.Request("http://127.0.0.1:8090/waapi", payload, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode("utf-8")) from error


if __name__ == "__main__":
    result = call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {},
                  json.loads(sys.argv[3]) if len(sys.argv) > 3 else {})
    print(json.dumps(result, ensure_ascii=False, indent=2))
