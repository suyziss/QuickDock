import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

def launch(entry):
    """Start an entry without invoking a shell. Returns (process, status_message)."""
    if entry.kind == "project":
        folder = Path(os.path.expanduser(entry.executable))
        if not folder.is_dir():
            return None, "Project folder does not exist"
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                opener = shutil.which("xdg-open")
                if not opener: return None, "xdg-open not found"
                subprocess.Popen([opener, str(folder)])
            return None, "project-opened"
        except OSError as exc:
            return None, str(exc)

    executable = os.path.expandvars(os.path.expanduser(entry.executable))
    if os.path.sep in executable and not os.path.exists(executable):
        return None, "Executable path does not exist"
    if os.path.sep not in executable and shutil.which(executable) is None:
        return None, f"Executable not found in PATH: {executable}"
    cwd = entry.working_dir or None
    if cwd and not os.path.isdir(cwd):
        return None, "Working directory does not exist"
    try:
        process = subprocess.Popen([executable, *map(str, entry.arguments)], cwd=cwd, shell=False)
        return process, "started"
    except (OSError, ValueError) as exc:
        return None, str(exc)

def split_arguments(text):
    return shlex.split(text, posix=(os.name != "nt"))
