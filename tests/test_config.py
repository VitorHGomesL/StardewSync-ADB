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

    def test_json_read_non_string_values_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "caminhos.json"
            config_file.write_text(
                json.dumps({"caminho_pc": None, "caminho_backup": 10}),
                encoding="utf-8",
            )

            with patch.object(config, "CONFIG_FILE", config_file):
                self.assertEqual(config.json_read(), (None, None))

    def test_configurar_caminhos_rejects_unsupported_system(self):
        with (
            patch("src.config.platform.system", return_value="Plan9"),
            patch("src.config.typer.echo"),
        ):
            with self.assertRaises(OSError):
                config.configurar_caminhos()

    def test_configurar_caminhos_uses_detected_saves_and_custom_backup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            home = tmpdir / "home"
            saves = home / ".config" / "StardewValley" / "Saves"
            backup = tmpdir / "backup"
            config_file = tmpdir / "caminhos.json"
            saves.mkdir(parents=True)

            with (
                patch.object(config, "CONFIG_FILE", config_file),
                patch("src.config.platform.system", return_value="Linux"),
                patch("src.config.Path.home", return_value=home),
                patch("builtins.input", side_effect=["", str(backup)]),
                patch("src.config.typer.echo"),
            ):
                config.configurar_caminhos()

                self.assertEqual(config.json_read(), (saves.resolve(), backup.resolve()))
                self.assertTrue(backup.is_dir())

    def test_configurar_caminhos_accepts_manual_saves_when_default_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            home = tmpdir / "home"
            manual_saves = tmpdir / "manual_saves"
            backup = tmpdir / "backup"
            config_file = tmpdir / "caminhos.json"
            manual_saves.mkdir()

            with (
                patch.object(config, "CONFIG_FILE", config_file),
                patch("src.config.platform.system", return_value="Linux"),
                patch("src.config.Path.home", return_value=home),
                patch("builtins.input", side_effect=[str(manual_saves), str(backup)]),
                patch("src.config.typer.echo"),
            ):
                config.configurar_caminhos()

                self.assertEqual(config.json_read(), (manual_saves.resolve(), backup.resolve()))
