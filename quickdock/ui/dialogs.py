from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit,
    QCheckBox, QDialogButtonBox)
from ..core.models import Entry
from ..core.launcher import split_arguments
from ..core.i18n import tr

class EntryDialog(QDialog):
    def __init__(self, parent=None, entry=None):
        super().__init__(parent)
        self.setWindowTitle(tr("edit") if entry else tr("add"))
        self.setMinimumWidth(430)
        layout = QFormLayout(self)
        self.name = QLineEdit(entry.name if entry else "")
        self.kind = QComboBox()
        self.kind.addItems(["command", "application", "script", "project"])
        if entry: self.kind.setCurrentText(entry.kind)
        self.executable = QLineEdit(entry.executable if entry else "")
        self.arguments = QTextEdit()
        if entry: self.arguments.setPlainText("\n".join(entry.arguments))
        self.cwd = QLineEdit(entry.working_dir if entry else "")
        self.favorite = QCheckBox(tr("favorite"))
        self.favorite.setChecked(entry.favorite if entry else False)
        layout.addRow(tr("name"), self.name)
        layout.addRow(tr("kind"), self.kind)
        layout.addRow(tr("executable"), self.executable)
        layout.addRow(tr("arguments"), self.arguments)
        layout.addRow(tr("working_dir"), self.cwd)
        layout.addRow("", self.favorite)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.entry_id = entry.id if entry else None

    def get_entry(self):
        args = []
        for line in self.arguments.toPlainText().splitlines():
            if line.strip(): args.extend(split_arguments(line))
        entry = Entry(self.name.text(), self.kind.currentText(), self.executable.text().strip(),
                      args, self.cwd.text().strip(), self.favorite.isChecked(), self.entry_id)
        entry.validate()
        return entry
