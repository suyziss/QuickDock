# QuickDock

Cross-platform launcher for commands, applications, scripts, and project folders.

**Platforms:** Windows, Linux, Android/Termux (CLI mode).  
**Languages:** English and Russian.

## Features
- Add, edit, delete, search and favorite launcher entries
- Entry types: `command`, `application`, `script`, `project`
- SQLite storage and JSON import/export
- Desktop GUI (PySide6) and terminal interface
- Run history
- Normal commands use `subprocess.Popen([...], shell=False)`

## Install

Python 3.10+ is required.

### Windows PowerShell
```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Android / Termux
```bash
pkg update
pkg install python
cd QuickDock
python main.py --cli
```
Termux mode uses Python standard-library components. Start the interactive TUI with `python main.py --tui`; the simpler text CLI remains available with `python main.py --cli`. The TUI supports keyboard navigation and terminal mouse events (tap support depends on whether the terminal app forwards mouse events). A regular Termux session does not provide the desktop environment expected by PySide6, so Android GUI is not included in this release.

## Run
```bash
python main.py          # desktop GUI
python main.py --tui    # interactive terminal UI (recommended)\npython main.py --cli    # basic terminal interface
python main.py --lang ru
python main.py --lang en --cli
```

## Add entries
- `command`: executable and arguments, e.g. executable `python`, argument `--version`
- `application`: application executable, e.g. `code`
- `script`: script file; specify its interpreter explicitly (e.g. executable `python`, argument `/path/to/script.py`)
- `project`: existing folder; opens it in the system file manager

Arguments in the GUI are entered one per line. In CLI mode, quote arguments containing spaces.

## Security
- QuickDock does not use a shell for normal commands.
- It does not elevate privileges or run as administrator/root.
- A command can still modify files or start other programs with your account permissions. Only add commands you trust.
- Project entries open folders; they do not execute project code.
- History records entry name, timestamp and status, not process output.

## Data
- Database: `~/.quickdock/quickdock.db`
- Log directory reserved at: `~/.quickdock/`

## Tests
```bash
python -m unittest discover -s tests -v
```

## Roadmap
- [x] Core launcher, SQLite storage, JSON backup
- [x] PySide6 desktop GUI
- [x] Termux CLI
- [x] RU/EN strings
- [ ] Native Android GUI
- [ ] Per-entry environment variables
- [ ] Application discovery and packaged releases

## License
MIT. See `LICENSE`.
