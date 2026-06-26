import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ui import caminho_configurado, status_atual


class TestUi(unittest.TestCase):
    def test_caminho_configurado_validates_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(caminho_configurado(Path(tmpdir)))
            self.assertFalse(caminho_configurado(Path(tmpdir) / "missing"))

    def test_status_atual_requires_configured_paths(self):
        self.assertEqual(
            status_atual(None, None),
            "Caminho do PC/Backup não configurado. Use o comando configurar e reinicie.",
        )

    @patch("src.ui.celular_conectado", return_value=False)
    def test_status_atual_reports_disconnected_phone(self, _celular_conectado):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "saves"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            self.assertEqual(
                status_atual(caminho_pc, caminho_backup),
                "Celular desconectado. Conecte o Android via USB com depuração ativada.",
            )

    @patch("src.ui.celular_conectado", return_value=True)
    def test_status_atual_reports_running_service(self, _celular_conectado):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "saves"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            self.assertEqual(status_atual(caminho_pc, caminho_backup), "Serviço em funcionamento!")
