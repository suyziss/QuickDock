# Platform notes

## Windows
Install Python 3.10+ and PySide6 for the desktop window. Executable names must be available in PATH or entered as absolute paths.

## Linux
Install Python 3.10+, PySide6, and a desktop file opener such as `xdg-open`. The GUI requires a graphical session. CLI mode works headlessly.

## Android / Termux
Use `python main.py --cli`. The project does not claim to provide a native Android GUI. Some Android apps cannot be launched like desktop executables; Termux commands and scripts are the intended CLI use case.
