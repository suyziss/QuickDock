from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox, QFileDialog, QComboBox)
from ..core.i18n import tr, set_language
from ..core.launcher import launch
from .dialogs import EntryDialog

class MainWindow(QMainWindow):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.setWindowTitle("QuickDock")
        self.resize(860, 590)
        self.setMinimumSize(650, 430)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        top = QHBoxLayout()
        brand = QLabel("⚡ QuickDock")
        brand.setObjectName("brand")
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("search"))
        self.search.textChanged.connect(self.refresh)
        self.lang = QComboBox()
        self.lang.addItems(["EN", "RU"])
        self.lang.currentIndexChanged.connect(self.change_language)
        top.addWidget(brand)
        top.addStretch()
        top.addWidget(self.search, 1)
        top.addWidget(self.lang)
        root.addLayout(top)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(lambda _: self.run_selected())
        root.addWidget(self.list, 1)
        actions = QHBoxLayout()
        self.action_buttons = []
        for label, callback in [
            ("＋ " + tr("add"), self.add_entry), ("▶ " + tr("run"), self.run_selected),
            ("✎ " + tr("edit"), self.edit_entry), ("⌫ " + tr("delete"), self.delete_entry)
        ]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            actions.addWidget(button)
            self.action_buttons.append(button)
        root.addLayout(actions)
        backup = QHBoxLayout()
        import_btn, export_btn = QPushButton(tr("import")), QPushButton(tr("export"))
        self.backup_buttons = [import_btn, export_btn]
        import_btn.clicked.connect(self.import_json)
        export_btn.clicked.connect(self.export_json)
        backup.addStretch()
        backup.addWidget(import_btn)
        backup.addWidget(export_btn)
        root.addLayout(backup)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #17191D; color: #E6E1E9; font-size: 14px; }
            QLabel#brand { color: #D0BCFF; font-size: 23px; font-weight: 700; padding: 8px; }
            QLineEdit, QTextEdit, QComboBox, QListWidget {
                background: #25282D; color: #E6E1E9; border: 1px solid #454850;
                border-radius: 12px; padding: 10px; selection-background-color: #6750A4;
            }
            QPushButton { background: #D0BCFF; color: #241A35; border: 0;
                border-radius: 15px; padding: 10px 15px; font-weight: 600; }
            QPushButton:hover { background: #E5D8FF; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #383B42; }
        """)
        self.refresh()

    def change_language(self, index):
        set_language("en" if index == 0 else "ru")
        labels = [("＋ " + tr("add")), ("▶ " + tr("run")), ("✎ " + tr("edit")), ("⌫ " + tr("delete"))]
        for button, label in zip(self.action_buttons, labels):
            button.setText(label)
        self.search.setPlaceholderText(tr("search"))
        self.backup_buttons[0].setText(tr("import"))
        self.backup_buttons[1].setText(tr("export"))

    def selected_entry(self):
        item = self.list.currentItem()
        return self.storage.get_entry(item.data(Qt.UserRole)) if item else None

    def refresh(self):
        self.list.clear()
        for entry in self.storage.list_entries(self.search.text().strip()):
            item = QListWidgetItem(f"{'★  ' if entry.favorite else ''}{entry.name}   ·   {entry.kind}\n{entry.executable}")
            item.setData(Qt.UserRole, entry.id)
            self.list.addItem(item)

    def add_entry(self):
        dialog = EntryDialog(self)
        if dialog.exec():
            try:
                self.storage.save_entry(dialog.get_entry())
                self.refresh()
            except Exception as exc: QMessageBox.warning(self, "QuickDock", str(exc))

    def edit_entry(self):
        entry = self.selected_entry()
        if not entry:
            QMessageBox.information(self, "QuickDock", tr("choose")); return
        dialog = EntryDialog(self, entry)
        if dialog.exec():
            try:
                self.storage.save_entry(dialog.get_entry())
                self.refresh()
            except Exception as exc: QMessageBox.warning(self, "QuickDock", str(exc))

    def delete_entry(self):
        entry = self.selected_entry()
        if not entry:
            QMessageBox.information(self, "QuickDock", tr("choose")); return
        if QMessageBox.question(self, "QuickDock", tr("confirm_delete")) == QMessageBox.Yes:
            self.storage.delete_entry(entry.id)
            self.refresh()

    def run_selected(self):
        entry = self.selected_entry()
        if not entry:
            QMessageBox.information(self, "QuickDock", tr("choose")); return
        if QMessageBox.question(self, "QuickDock", f"{tr('run')} '{entry.name}'?") != QMessageBox.Yes:
            return
        process, message = launch(entry)
        if process:
            self.storage.add_history(entry.name, None)
            QMessageBox.information(self, "QuickDock", f"{tr('run_started')}{entry.name}\\nPID: {process.pid}")
        elif message == "project-opened":
            self.storage.add_history(entry.name, 0)
            QMessageBox.information(self, "QuickDock", tr("project_opened"))
        else:
            self.storage.add_history(entry.name, -1)
            QMessageBox.warning(self, "QuickDock", f"{tr('run_failed')}{message}")

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "JSON (*.json)")
        if path:
            try:
                count = self.storage.import_json(path)
                self.refresh()
                QMessageBox.information(self, "QuickDock", f"Imported: {count}")
            except Exception as exc: QMessageBox.warning(self, "QuickDock", str(exc))

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export", "quickdock-backup.json", "JSON (*.json)")
        if path:
            try:
                self.storage.export_json(path)
                QMessageBox.information(self, "QuickDock", "Export complete")
            except Exception as exc: QMessageBox.warning(self, "QuickDock", str(exc))
