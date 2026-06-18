import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _python_executable() -> str:
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    return sys.executable


def main(argv: list[str] | None = None) -> int:
    python = _python_executable()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (
        f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
    )
    command = [
        python,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "frontend" / "app.py"),
        *(argv or []),
    ]
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
