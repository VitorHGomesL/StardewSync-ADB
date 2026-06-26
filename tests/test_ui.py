import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ui import caminho_configurado, show_banner, status_atual


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

    @patch("src.ui.celular_conectado")
    def test_status_atual_does_not_check_android_when_paths_are_invalid(self, celular_conectado):
        self.assertEqual(
            status_atual(Path("/tmp/nao-existe"), Path("/tmp/tambem-nao-existe")),
            "Caminho do PC/Backup não configurado. Use o comando configurar e reinicie.",
        )
        celular_conectado.assert_not_called()

    def test_show_banner_returns_renderable_group_without_configured_paths(self):
        banner = show_banner(
            None,
            None,
            "Caminho do PC/Backup não configurado",
            tela="",
            android_conectado=False,
            android_status_texto="ADB não encontrado",
        )

        self.assertEqual(len(banner.renderables), 2)
