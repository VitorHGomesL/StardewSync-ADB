import inspect
import unittest
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

import main


class TestCliCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_caminhos_command_prints_configured_paths(self):
        with (
            patch.object(main, "CAMINHO_PC", Path("/tmp/pc")),
            patch.object(main, "CAMINHO_BACKUP", Path("/tmp/backup")),
        ):
            resultado = self.runner.invoke(main.app, ["caminhos"])

        self.assertEqual(resultado.exit_code, 0)
        self.assertIn("Caminho do PC: /tmp/pc", resultado.stdout)
        self.assertIn("Caminho do Backup: /tmp/backup", resultado.stdout)

    def test_config_command_delegates_to_configurar_caminhos(self):
        with patch.object(main, "configurar_caminhos") as configurar_caminhos:
            resultado = self.runner.invoke(main.app, ["config"])

        self.assertEqual(resultado.exit_code, 0)
        configurar_caminhos.assert_called_once_with()

    def test_main_does_not_reactivate_watchdog(self):
        fonte = inspect.getsource(main)

        self.assertNotIn("vigiar_alteracoes", fonte)
        self.assertNotIn("src.watchdog", fonte)
