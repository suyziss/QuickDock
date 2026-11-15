import tempfile
import unittest
from pathlib import Path
from quickdock.core.models import Entry
from quickdock.core.storage import Storage
from quickdock.core.launcher import split_arguments

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self.tmp.name) / "test.db")
    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()
    def test_save_and_list(self):
        self.storage.save_entry(Entry("Python version", "command", "python", ["--version"]))
        self.assertEqual(self.storage.list_entries()[0].name, "Python version")
    def test_import_export(self):
        e = Entry("Example", "command", "python", ["-V"], favorite=True)
        self.storage.save_entry(e)
        backup = Path(self.tmp.name) / "backup.json"
        self.storage.export_json(backup)
        self.storage.delete_entry(e.id)
        self.assertEqual(self.storage.import_json(backup), 1)
        self.assertEqual(self.storage.list_entries()[0].name, "Example")
    def test_split_arguments(self):
        self.assertEqual(split_arguments('--label "hello world"'), ["--label", "hello world"])

if __name__ == "__main__":
    unittest.main()
