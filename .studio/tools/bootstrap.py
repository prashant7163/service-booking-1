from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def _result(code: str, summary: str, *, next_action: str | None = None) -> int:
    payload = {"code": code, "summary": summary}
    if next_action is not None:
        payload["next_action"] = next_action
    print(json.dumps(payload, indent=2, sort_keys=True))
    return {
        "ok": 0,
        "invalid_input": 2,
        "policy_denied": 4,
        "state_corrupt": 5,
    }[code]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(root: Path) -> dict[str, Any]:
    path = root / ".studio/tools/tool-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("tool manifest must be a JSON object")
    return payload


def _uv_version(executable: str) -> tuple[int, ...]:
    output = subprocess.run(
        [executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", output)
    if match is None:
        raise ValueError("uv version could not be determined")
    return tuple(int(part) for part in match.groups())


def bootstrap(project_root: Path) -> int:
    root = project_root.resolve(strict=True)
    try:
        manifest = _manifest(root)
        tools = root / ".studio/tools"
        wheel = tools / str(manifest["wheel"]["file"])
        lock = tools / str(manifest["lock"]["file"])
        if _digest(wheel) != manifest["wheel"]["sha256"]:
            return _result(
                "state_corrupt",
                "Pinned Studio wheel digest does not match tool-manifest.json.",
            )
        if _digest(lock) != manifest["lock"]["sha256"]:
            return _result(
                "state_corrupt",
                "Pinned Studio lock digest does not match tool-manifest.json.",
            )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        return _result("invalid_input", f"Bootstrap metadata is invalid: {str(error)[:300]}")

    uv = shutil.which("uv")
    if uv is None:
        return _result(
            "policy_denied",
            "A compatible existing uv executable is required; Studio will not download it.",
            next_action="Install an approved uv release and rerun ./studioctl bootstrap.",
        )
    try:
        if _uv_version(uv) < (0, 12, 0):
            return _result(
                "policy_denied",
                "The available uv release is incompatible with this Studio bundle.",
                next_action="Install uv 0.12 or newer through the approved system path.",
            )
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        return _result("invalid_input", f"Unable to verify uv: {str(error)[:300]}")

    runtime = root / ".studio/runtime"
    python = runtime / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if python.is_file():
        return _result("ok", "Project-local Studio runtime is already bootstrapped.")

    staging = root / ".studio" / f".runtime-staging-{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    environment = dict(os.environ)
    environment["UV_PYTHON_DOWNLOADS"] = "never"
    try:
        created = subprocess.run(
            [uv, "venv", "--python", "3.12", "--no-python-downloads", str(staging)],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if created.returncode != 0:
            return _result(
                "policy_denied",
                "A compatible local Python 3.12 interpreter is required.",
                next_action="Install Python 3.12 locally; bootstrap will not download it.",
            )
        staging_python = staging / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        installed = subprocess.run(
            [
                uv,
                "pip",
                "install",
                "--python",
                str(staging_python),
                "--offline",
                str(wheel),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if installed.returncode != 0:
            return _result(
                "policy_denied",
                "Locked runtime dependencies are not fully cached; network access is required.",
                next_action=(
                    "Approve dependency retrieval, populate the uv cache, and rerun bootstrap."
                ),
            )
        os.replace(staging, runtime)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return _result("ok", "Project-local Studio runtime bootstrapped from verified pinned assets.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="studio-bootstrap")
    parser.add_argument("--project-root", type=Path, required=True)
    arguments = parser.parse_args(argv)
    return bootstrap(arguments.project_root)


if __name__ == "__main__":
    sys.exit(main())
