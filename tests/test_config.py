import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import src.config as config


class TestConfigJson(unittest.TestCase):
    def test_json_read_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "caminhos.json"

            with patch.object(config, "CONFIG_FILE", config_file):
                self.assertEqual(config.json_read(), (None, None))

    def test_json_write_and_read_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_file = tmpdir / "caminhos.json"
            saves = tmpdir / "saves"
            backups = tmpdir / "backups"
            saves.mkdir()
            backups.mkdir()

            with patch.object(config, "CONFIG_FILE", config_file):
                config.json_write(saves, backups)

                self.assertEqual(config.json_read(), (saves.resolve(), backups.resolve()))

    def test_json_read_empty_values_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "caminhos.json"
            config_file.write_text(
                json.dumps({"caminho_pc": "", "caminho_backup": ""}),
                encoding="utf-8",
            )

            with patch.object(config, "CONFIG_FILE", config_file):
                self.assertEqual(config.json_read(), (None, None))

    def test_json_read_invalid_json_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "caminhos.json"
            config_file.write_text("{", encoding="utf-8")

            with patch.object(config, "CONFIG_FILE", config_file):
                self.assertEqual(config.json_read(), (None, None))

    @unittest.expectedFailure
    def test_json_read_non_string_values_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "caminhos.json"
            config_file.write_text(
                json.dumps({"caminho_pc": None, "caminho_backup": 10}),
                encoding="utf-8",
            )

            with patch.object(config, "CONFIG_FILE", config_file):
                self.assertEqual(config.json_read(), (None, None))
