import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

from src.backup import realizar_backup, tempo_pc


class TestBackup(unittest.TestCase):
    def test_tempo_pc_returns_zero_for_missing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing"

            self.assertEqual(tempo_pc(missing), 0)

    def test_tempo_pc_returns_newest_nested_file_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            saves = Path(tmpdir) / "saves"
            nested = saves / "Player_123"
            nested.mkdir(parents=True)
            old_file = saves / "old"
            new_file = nested / "new"
            old_file.write_text("old", encoding="utf-8")
            new_file.write_text("new", encoding="utf-8")
            old_time = 1000
            new_time = 2000

            os.utime(saves, (900, 900))
            os.utime(nested, (1500, 1500))
            os.utime(old_file, (old_time, old_time))
            os.utime(new_file, (new_time, new_time))

            self.assertEqual(tempo_pc(saves), new_time)

    def test_realizar_backup_copies_pc_when_pc_is_newer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            saves = tmpdir / "saves"
            backup = tmpdir / "backup"
            saves.mkdir()
            backup.mkdir()
            (saves / "save").write_text("pc", encoding="utf-8")

            with patch("src.adb.tempo_celular", return_value=0):
                realizar_backup(saves, backup, saves)

            self.assertEqual((backup / "save").read_text(encoding="utf-8"), "pc")
