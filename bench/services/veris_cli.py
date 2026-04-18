"""Optional subprocess bridge to the Veris CLI (installed via pipx / venv).

Requires ``veris`` on PATH (often ``~/.local/bin`` after ``pipx``). Override with env
``VERIS_CLI_PATH``. Full simulations still need ``veris env push`` etc. — see docs/VERIS_STEPS.md.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any


def _is_executable_file(path: str) -> bool:
    return bool(path and os.path.isfile(path) and os.access(path, os.X_OK))


def _candidate_veris_paths() -> list[str]:
    """pipx installs to ~/.local/bin; IDE-launched Django often omits that from PATH."""
    home = os.path.expanduser("~")
    return [
        os.path.join(home, ".local", "bin", "veris"),
        os.path.join(home, ".local", "pipx", "venvs", "veris-cli", "bin", "veris"),
        os.path.join(home, "bin", "veris"),
        "/usr/local/bin/veris",
    ]


def veris_binary() -> str | None:
    override = os.environ.get("VERIS_CLI_PATH", "").strip()
    if override and _is_executable_file(override):
        return override

    found = shutil.which("veris")
    if found:
        return found

    for path in _candidate_veris_paths():
        if _is_executable_file(path):
            return path

    return None


def run_veris(args: list[str], *, timeout: float = 90.0) -> dict[str, Any]:
    binary = veris_binary()
    if not binary:
        return {
            "ok": False,
            "error": "veris CLI not found. Install with pipx (see docs/VERIS_STEPS.md) and ensure "
            "~/.local/bin is on PATH, or set VERIS_CLI_PATH.",
        }
    cmd = [binary, *args]
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout after {timeout}s", "command": cmd}
    except Exception as e:
        return {"ok": False, "error": str(e), "command": cmd}

    return {
        "ok": r.returncode == 0,
        "returncode": r.returncode,
        "stdout": r.stdout,
        "stderr": r.stderr,
        "command": cmd,
    }
