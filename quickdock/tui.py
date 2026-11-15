"""Interactive QuickDock terminal UI with keyboard and terminal mouse support."""
import curses
import os
import textwrap
from .core.i18n import tr
from .core.models import Entry
from .core.launcher import launch, split_arguments

EN = {
    "title": "QUICKDOCK", "subtitle": "Your commands, apps and projects",
    "all": "ALL", "fav": "FAVORITES", "history": "HISTORY",
    "add": "Add", "run": "Open / Run", "edit": "Edit", "delete": "Delete",
    "favorite": "Toggle favorite", "search": "Search", "quit": "Quit",
    "empty": "No entries yet. Press A to add one.",
    "keys": "↑/↓ navigate   Enter run   A add   E edit   D delete   F favorite   / search   H history   Q quit",
    "name": "Name: ", "kind": "Type (command/application/script/project): ",
    "exe": "Executable or path: ", "args": "Arguments (quoted, optional): ",
    "cwd": "Working directory (optional): ", "fav_prompt": "Favorite? (y/N): ",
    "saved": "Saved.", "deleted": "Deleted.", "fav_done": "Favorite updated.",
    "confirm": "Delete selected entry? (y/N): ", "run_confirm": "Run selected entry? (y/N): ",
    "started": "Started: ", "opened": "Project folder opened.",
    "failed": "Could not start: ", "filter": "Search: ", "no_match": "No matching entries.",
    "history_title": "RECENT ACTIVITY", "back": "Press any key to return.",
    "invalid": "Invalid input: ", "mouse": "Touch/click support depends on terminal mouse reporting.",
}
RU = {
    "title": "QUICKDOCK", "subtitle": "Команды, приложения и проекты",
    "all": "ВСЕ", "fav": "ИЗБРАННОЕ", "history": "ИСТОРИЯ",
    "add": "Добавить", "run": "Открыть / Запуск", "edit": "Изменить", "delete": "Удалить",
    "favorite": "В избранное", "search": "Поиск", "quit": "Выход",
    "empty": "Записей пока нет. Нажми A, чтобы добавить.",
    "keys": "↑/↓ навигация   Enter запуск   A добавить   E изменить   D удалить   F избранное   / поиск   H история   Q выход",
    "name": "Название: ", "kind": "Тип (command/application/script/project): ",
    "exe": "Программа или путь: ", "args": "Аргументы (в кавычках, необязательно): ",
    "cwd": "Рабочая папка (необязательно): ", "fav_prompt": "В избранное? (y/N): ",
    "saved": "Сохранено.", "deleted": "Удалено.", "fav_done": "Избранное обновлено.",
    "confirm": "Удалить выбранную запись? (y/N): ", "run_confirm": "Запустить выбранную запись? (y/N): ",
    "started": "Запущено: ", "opened": "Папка проекта открыта.",
    "failed": "Не удалось запустить: ", "filter": "Поиск: ", "no_match": "Совпадений нет.",
    "history_title": "НЕДАВНЯЯ АКТИВНОСТЬ", "back": "Нажми любую клавишу для возврата.",
    "invalid": "Некорректные данные: ", "mouse": "Касания зависят от поддержки событий мыши терминалом.",
}

class QuickDockTUI:
    def __init__(self, stdscr, storage, language="en"):
        self.s = stdscr
        self.storage = storage
        self.lang = RU if language == "ru" else EN
        self.selected = 0
        self.filter = ""
        self.favorites_only = False
        self.status = self.lang["mouse"]
        self.entries = []
        self.row_to_entry = {}

    def t(self, key):
        return self.lang.get(key, key)

    def safe_add(self, y, x, value, attr=0, width=None):
        try:
            value = str(value)
            if width is not None:
                value = value[:max(0, width)]
            self.s.addnstr(y, x, value, max(0, width if width is not None else curses.COLS - x - 1), attr)
        except curses.error:
            pass

    def prompt(self, label, default=""):
        h, w = self.s.getmaxyx()
        self.s.addstr(h - 2, 1, " " * max(1, w - 2))
        self.safe_add(h - 2, 1, label + default, curses.A_BOLD, w - 3)
        curses.echo()
        curses.curs_set(1)
        try:
            raw = self.s.getstr(h - 2, min(w - 2, len(label) + len(default) + 1), max(1, w - len(label) - len(default) - 4))
            value = raw.decode("utf-8", "replace").strip()
        finally:
            curses.noecho()
            curses.curs_set(0)
        return value if value else default

    def message(self, value):
        self.status = value
        self.s.timeout(-1)
        self.s.getch()
        self.s.timeout(150)

    def refresh_entries(self):
        self.entries = self.storage.list_entries(self.filter)
        if self.favorites_only:
            self.entries = [e for e in self.entries if e.favorite]
        self.selected = min(self.selected, max(0, len(self.entries) - 1))

    def draw(self):
        self.s.erase()
        h, w = self.s.getmaxyx()
        title = self.t("title")
        self.safe_add(0, 2, "╭" + "─" * max(0, w - 6) + "╮", curses.A_DIM)
        self.safe_add(1, 3, "◆ " + title + "  /  " + self.t("subtitle"), curses.A_BOLD)
        tabs = "[ " + self.t("all") + " ]   [ " + self.t("fav") + " ]"
        self.safe_add(3, 2, tabs, curses.A_REVERSE if not self.favorites_only else curses.A_NORMAL)
        self.safe_add(4, 2, self.t("filter") + (self.filter or "—"), curses.A_DIM)
        self.safe_add(5, 2, "─" * max(0, w - 4), curses.A_DIM)
        self.row_to_entry = {}
        if not self.entries:
            self.safe_add(7, 3, self.t("empty") if not self.filter else self.t("no_match"), curses.A_DIM)
        else:
            visible = max(1, h - 10)
            start = max(0, min(self.selected - visible + 1, len(self.entries) - visible))
            for offset, entry in enumerate(self.entries[start:start + visible]):
                y = 6 + offset
                self.row_to_entry[y] = start + offset
                marker = "★" if entry.favorite else " "
                line = f" {marker}  {entry.name}   ·   {entry.kind}"
                attr = curses.A_REVERSE | curses.A_BOLD if start + offset == self.selected else curses.A_NORMAL
                self.safe_add(y, 2, line, attr, w - 4)
        self.safe_add(h - 3, 2, self.status, curses.A_DIM, w - 4)
        self.safe_add(h - 2, 2, self.t("keys"), curses.A_BOLD, w - 4)
        self.s.refresh()

    def selected_entry(self):
        return self.entries[self.selected] if self.entries else None

    def add_or_edit(self, entry=None):
        old = entry
        name = self.prompt(self.t("name"), old.name if old else "")
        if not name: return
        kind = self.prompt(self.t("kind"), old.kind if old else "command").lower()
        if kind not in ("command", "application", "script", "project"):
            self.message(self.t("invalid") + kind); return
        executable = self.prompt(self.t("exe"), old.executable if old else "")
        if not executable: return
        old_args = " ".join(__import__("shlex").quote(x) for x in old.arguments) if old else ""
        args_text = self.prompt(self.t("args"), old_args)
        cwd = self.prompt(self.t("cwd"), old.working_dir if old else "")
        fav = self.prompt(self.t("fav_prompt"), "y" if old and old.favorite else "n").lower() == "y"
        try:
            args = split_arguments(args_text)
            item = Entry(name, kind, executable, args, cwd, fav, old.id if old else None)
            self.storage.save_entry(item)
            self.status = self.t("saved")
            self.refresh_entries()
        except Exception as exc:
            self.message(self.t("invalid") + str(exc))

    def run_selected(self):
        entry = self.selected_entry()
        if not entry: return
        if self.prompt(self.t("run_confirm"), "y").lower() != "y": return
        process, result = launch(entry)
        if process:
            self.storage.add_history(entry.name, None)
            self.status = self.t("started") + entry.name + f" (PID {process.pid})"
        elif result == "project-opened":
            self.storage.add_history(entry.name, 0)
            self.status = self.t("opened")
        else:
            self.storage.add_history(entry.name, -1)
            self.status = self.t("failed") + result

    def show_history(self):
        rows = self.storage.list_history(20)
        self.s.erase()
        h, w = self.s.getmaxyx()
        self.safe_add(1, 2, self.t("history_title"), curses.A_BOLD)
        for i, row in enumerate(rows[:max(1, h - 5)]):
            self.safe_add(3 + i, 2, f"{row['started_at']}  ·  {row['entry_name']}  ·  {row['return_code']}", width=w - 4)
        self.safe_add(h - 2, 2, self.t("back"), curses.A_DIM)
        self.s.refresh()
        self.s.timeout(-1); self.s.getch(); self.s.timeout(150)

    def handle_mouse(self):
        try:
            _, mx, my, _, state = curses.getmouse()
        except curses.error:
            return
        if my in self.row_to_entry:
            self.selected = self.row_to_entry[my]
            if state & getattr(curses, "BUTTON1_DOUBLE_CLICKED", 0):
                self.run_selected()
            elif state & getattr(curses, "BUTTON1_CLICKED", 0):
                self.status = self.entries[self.selected].name

    def loop(self):
        curses.curs_set(0)
        self.s.keypad(True)
        self.s.timeout(150)
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except (AttributeError, curses.error):
            pass
        self.refresh_entries()
        while True:
            self.draw()
            key = self.s.getch()
            if key == -1: continue
            if key == curses.KEY_MOUSE:
                self.handle_mouse()
            elif key in (curses.KEY_UP, ord("k")):
                self.selected = max(0, self.selected - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                self.selected = min(max(0, len(self.entries) - 1), self.selected + 1)
            elif key in (10, 13, curses.KEY_ENTER):
                self.run_selected()
            elif key in (ord("a"), ord("A")):
                self.add_or_edit()
            elif key in (ord("e"), ord("E")):
                if self.selected_entry(): self.add_or_edit(self.selected_entry())
            elif key in (ord("d"), ord("D")):
                entry = self.selected_entry()
                if entry and self.prompt(self.t("confirm"), "n").lower() == "y":
                    self.storage.delete_entry(entry.id); self.status = self.t("deleted"); self.refresh_entries()
            elif key in (ord("f"), ord("F")):
                entry = self.selected_entry()
                if entry:
                    entry.favorite = not entry.favorite
                    self.storage.save_entry(entry); self.status = self.t("fav_done"); self.refresh_entries()
            elif key == ord("/"):
                self.filter = self.prompt(self.t("filter"), self.filter); self.selected = 0; self.refresh_entries()
            elif key in (ord("h"), ord("H")):
                self.show_history()
            elif key in (ord("t"), ord("T")):
                self.favorites_only = not self.favorites_only; self.selected = 0; self.refresh_entries()
            elif key in (ord("q"), ord("Q"), 27):
                break

def run_tui(storage, language="en"):
    try:
        curses.wrapper(lambda stdscr: QuickDockTUI(stdscr, storage, language).loop())
    except (curses.error, OSError) as exc:
        print(f"QuickDock TUI unavailable: {exc}")
        print("Try: python main.py --cli")
