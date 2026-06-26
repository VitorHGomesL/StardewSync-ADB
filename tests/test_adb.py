import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import src.adb as adb


class TestAdb(unittest.TestCase):
    @patch("src.adb.shutil.which", return_value="/usr/bin/adb")
    def test_encontrar_adb_uses_system_adb(self, _which):
        self.assertEqual(adb.encontrar_adb(), Path("/usr/bin/adb"))

    @patch("src.adb.shutil.which", return_value=None)
    @patch("src.adb.Path.exists", return_value=False)
    def test_encontrar_adb_raises_when_missing(self, _exists, _which):
        with self.assertRaises(FileNotFoundError):
            adb.encontrar_adb()

    @patch("src.adb.encontrar_adb", side_effect=FileNotFoundError)
    def test_diagnosticar_android_without_adb(self, _encontrar_adb):
        self.assertEqual(adb.diagnosticar_android(), (False, "ADB não encontrado"))

    @patch("src.adb.adb_shell")
    @patch("src.adb.adb_run")
    @patch("src.adb.encontrar_adb", return_value=Path("/usr/bin/adb"))
    def test_diagnosticar_android_connected(self, _encontrar_adb, adb_run, _adb_shell):
        adb_run.return_value = Mock(stdout="List of devices attached\nabc\tdevice\n")

        self.assertEqual(
            adb.diagnosticar_android(),
            (True, "Android conectado e caminho disponível"),
        )

    @patch("src.adb.adb_run")
    @patch("src.adb.encontrar_adb", return_value=Path("/usr/bin/adb"))
    def test_diagnosticar_android_without_devices(self, _encontrar_adb, adb_run):
        adb_run.return_value = Mock(stdout="List of devices attached\n")

        self.assertEqual(
            adb.diagnosticar_android(),
            (False, "Nenhum dispositivo ADB conectado"),
        )

    @patch("src.adb.adb_shell")
    def test_tempo_celular_returns_zero_on_adb_error(self, adb_shell):
        adb_shell.side_effect = subprocess.CalledProcessError(1, ["adb"])

        self.assertEqual(adb.tempo_celular(), 0)

    @patch("src.adb.adb_shell", return_value=Mock(stdout="123\n"))
    def test_tempo_celular_returns_timestamp(self, _adb_shell):
        self.assertEqual(adb.tempo_celular(), 123)

    @patch("src.adb.adb_pull")
    @patch("src.adb.tempo_celular", return_value=200)
    @patch("src.adb.celular_conectado", return_value=True)
    @patch("src.backup.tempo_pc", return_value=100)
    def test_sincronia_inicial_pulls_when_android_is_newer(
        self,
        _tempo_pc,
        _celular_conectado,
        _tempo_celular,
        adb_pull,
    ):
        caminho_pc = Path("/tmp/saves")

        resultado = adb.sincronia_inicial(caminho_pc)

        self.assertEqual(resultado, "PC atualizado com o save do celular")
        adb_pull.assert_called_once_with(adb.CAMINHO_CELULAR, caminho_pc)
