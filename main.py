import argparse
import sys
from quickdock.core.i18n import set_language, tr
from quickdock.core.storage import Storage

def main():
    parser = argparse.ArgumentParser(description="QuickDock launcher")
    parser.add_argument("--cli", action="store_true", help="Use basic terminal interface")
    parser.add_argument("--tui", action="store_true", help="Use interactive terminal interface")
    parser.add_argument("--lang", choices=("en", "ru"), default=None)
    args = parser.parse_args()
    set_language(args.lang)
    storage = Storage()
    if args.tui:
        from quickdock.tui import run_tui
        run_tui(storage, args.lang or "en")
        return
    if args.cli:
        from quickdock.cli import run_cli
        run_cli(storage)
        return
    try:
        from PySide6.QtWidgets import QApplication
        from quickdock.ui.main_window import MainWindow
    except ImportError:
        print(tr("qt_missing"))
        print(tr("cli_hint"))
        return
    app = QApplication(sys.argv)
    app.setApplicationName("QuickDock")
    window = MainWindow(storage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
