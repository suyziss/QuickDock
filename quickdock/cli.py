from .core.i18n import tr
from .core.models import Entry
from .core.launcher import launch, split_arguments

def run_cli(storage):
    while True:
        entries = storage.list_entries()
        print("\n=== QuickDock ===")
        if not entries: print(tr("no_entries"))
        for i, e in enumerate(entries, 1):
            print(f"{i}. {'★ ' if e.favorite else ''}{e.name} [{e.kind}]")
        choice = input("\nA) Add  R) Run  D) Delete  Q) Quit\n> ").strip().lower()
        if choice == "q": break
        if choice == "a":
            try:
                entry = Entry(input("Name: ").strip(), input("Type (command/application/script/project): ").strip().lower(),
                    input("Executable/path: ").strip(), split_arguments(input("Arguments: ")),
                    input("Working directory (optional): ").strip(),
                    input("Favorite? [y/N]: ").strip().lower() == "y")
                storage.save_entry(entry)
                print(tr("done"))
            except Exception as exc: print(f"Error: {exc}")
        elif choice in ("r", "d"):
            try:
                index = int(input("Entry number: ")) - 1
                entry = entries[index]
                if choice == "d":
                    if input(f"Delete '{entry.name}'? [y/N]: ").lower() == "y":
                        storage.delete_entry(entry.id)
                        print(tr("deleted"))
                elif input(f"Run '{entry.name}'? [y/N]: ").lower() == "y":
                    process, message = launch(entry)
                    if process:
                        storage.add_history(entry.name, None)
                        print(f"{tr('run_started')}{entry.name} (PID {process.pid})")
                    elif message == "project-opened":
                        storage.add_history(entry.name, 0)
                        print(tr("project_opened"))
                    else:
                        storage.add_history(entry.name, -1)
                        print(f"{tr('run_failed')}{message}")
            except (ValueError, IndexError) as exc: print(f"Error: {exc}")
