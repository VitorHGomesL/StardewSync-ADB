import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config import CAMINHO_CELULAR
from src.sync import sincronizar_manual


class TestSyncManual(unittest.TestCase):
    def test_sincronizar_manual_requires_configured_paths(self):
        resultado = sincronizar_manual(None, None)

        self.assertEqual(
            resultado,
            "Caminho do PC/Backup não configurado.\nUse: python3 main.py config",
        )

    @patch("src.sync.diagnosticar_android", return_value=(False, "Nenhum dispositivo ADB conectado"))
    def test_sincronizar_manual_reports_disconnected_android(self, diagnosticar_android):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Android desconectado.\nConecte o celular via USB com depuração ativada.",
        )
        diagnosticar_android.assert_called_once_with()

    @patch("src.sync.tempo_celular", return_value=0)
    @patch("src.sync.tempo_pc", return_value=0)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_pull")
    @patch("src.sync.adb_push")
    def test_sincronizar_manual_stops_when_times_cannot_be_compared(
        self,
        adb_push,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Não foi possível comparar os saves.\nVerifique os caminhos do PC e do Android.",
        )
        realizar_backup.assert_not_called()
        adb_pull.assert_not_called()
        adb_push.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=100)
    @patch("src.sync.tempo_pc", return_value=100)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_pull")
    @patch("src.sync.adb_push")
    def test_sincronizar_manual_does_nothing_when_saves_are_synced(
        self,
        adb_push,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(resultado, "Saves já estão sincronizados.\nNada foi alterado.")
        realizar_backup.assert_not_called()
        adb_pull.assert_not_called()
        adb_push.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=100)
    @patch("src.sync.tempo_pc", return_value=200)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_push")
    def test_sincronizar_manual_sends_pc_save_to_android_when_pc_is_newer(
        self,
        adb_push,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Android conectado.\nBackup criado.\nPC mais recente.\nSave enviado para o Android.",
        )
        realizar_backup.assert_called_once_with(caminho_pc, caminho_backup, caminho_pc)
        adb_push.assert_called_once_with(caminho_pc, CAMINHO_CELULAR)

    @patch("src.sync.tempo_celular", return_value=100)
    @patch("src.sync.tempo_pc", return_value=200)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup", side_effect=Exception("sem permissão"))
    @patch("src.sync.adb_push")
    def test_sincronizar_manual_cancela_push_se_backup_falhar(
        self,
        adb_push,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Falha ao criar backup.\nSincronização cancelada.\nErro: sem permissão",
        )
        realizar_backup.assert_called_once_with(caminho_pc, caminho_backup, caminho_pc)
        adb_push.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=100)
    @patch("src.sync.tempo_pc", return_value=200)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup", return_value=False)
    @patch("src.sync.adb_push")
    def test_sincronizar_manual_cancela_push_se_backup_retornar_falso(
        self,
        adb_push,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(resultado, "Falha ao criar backup.\nSincronização cancelada.")
        realizar_backup.assert_called_once_with(caminho_pc, caminho_backup, caminho_pc)
        adb_push.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=100)
    @patch("src.sync.tempo_pc", return_value=200)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_push", side_effect=Exception("falha adb"))
    def test_sincronizar_manual_informa_erro_quando_push_falha(
        self,
        adb_push,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Falha ao enviar save para o Android.\nBackup foi mantido.\nErro: falha adb",
        )
        realizar_backup.assert_called_once_with(caminho_pc, caminho_backup, caminho_pc)
        adb_push.assert_called_once_with(caminho_pc, CAMINHO_CELULAR)

    @patch("src.sync.tempo_celular", return_value=200)
    @patch("src.sync.tempo_pc", return_value=100)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_pull")
    def test_sincronizar_manual_pulls_android_save_when_android_is_newer(
        self,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Android conectado.\nBackup criado.\nAndroid mais recente.\nSave puxado para o PC.",
        )
        realizar_backup.assert_called_once_with(CAMINHO_CELULAR, caminho_backup, caminho_pc)
        adb_pull.assert_called_once_with(CAMINHO_CELULAR, caminho_pc)

    @patch("src.sync.tempo_celular", return_value=200)
    @patch("src.sync.tempo_pc", return_value=100)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup", side_effect=Exception("disco cheio"))
    @patch("src.sync.adb_pull")
    def test_sincronizar_manual_cancela_pull_se_backup_falhar(
        self,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Falha ao criar backup.\nSincronização cancelada.\nErro: disco cheio",
        )
        realizar_backup.assert_called_once_with(CAMINHO_CELULAR, caminho_backup, caminho_pc)
        adb_pull.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=200)
    @patch("src.sync.tempo_pc", return_value=100)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup", return_value=False)
    @patch("src.sync.adb_pull")
    def test_sincronizar_manual_cancela_pull_se_backup_retornar_falso(
        self,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(resultado, "Falha ao criar backup.\nSincronização cancelada.")
        realizar_backup.assert_called_once_with(CAMINHO_CELULAR, caminho_backup, caminho_pc)
        adb_pull.assert_not_called()

    @patch("src.sync.tempo_celular", return_value=200)
    @patch("src.sync.tempo_pc", return_value=100)
    @patch("src.sync.diagnosticar_android", return_value=(True, "Android conectado e caminho disponível"))
    @patch("src.sync.realizar_backup")
    @patch("src.sync.adb_pull", side_effect=Exception("falha adb"))
    def test_sincronizar_manual_informa_erro_quando_pull_falha(
        self,
        adb_pull,
        realizar_backup,
        _diagnosticar_android,
        _tempo_pc,
        _tempo_celular,
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_pc = Path(tmpdir) / "pc"
            caminho_backup = Path(tmpdir) / "backup"
            caminho_pc.mkdir()
            caminho_backup.mkdir()

            resultado = sincronizar_manual(caminho_pc, caminho_backup)

        self.assertEqual(
            resultado,
            "Falha ao puxar save do Android.\nBackup foi mantido.\nErro: falha adb",
        )
        realizar_backup.assert_called_once_with(CAMINHO_CELULAR, caminho_backup, caminho_pc)
        adb_pull.assert_called_once_with(CAMINHO_CELULAR, caminho_pc)
