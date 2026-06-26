import unittest
from pathlib import Path
from unittest.mock import patch

import src.watchdog as watchdog


class TestWatchdog(unittest.TestCase):
    def test_vigiar_alteracoes_returns_without_config(self):
        with (
            patch.object(watchdog, "CAMINHO_PC", None),
            patch.object(watchdog, "CAMINHO_BACKUP", None),
            patch.object(watchdog, "tempo_pc") as tempo_pc,
            patch.object(watchdog.typer, "echo"),
        ):
            watchdog.vigiar_alteracoes()

            tempo_pc.assert_not_called()

    def test_vigiar_alteracoes_stops_when_phone_disconnects(self):
        with (
            patch.object(watchdog, "CAMINHO_PC", Path("/tmp/saves")),
            patch.object(watchdog, "CAMINHO_BACKUP", Path("/tmp/backup")),
            patch.object(watchdog, "celular_conectado", return_value=False),
            patch.object(watchdog, "tempo_pc", return_value=1),
            patch.object(watchdog.time, "sleep") as sleep,
            patch.object(watchdog.os, "system") as system,
            patch.object(watchdog.typer, "echo"),
        ):
            watchdog.vigiar_alteracoes()

            sleep.assert_not_called()
            system.assert_not_called()

    def test_vigiar_alteracoes_uses_current_function_signatures(self):
        with (
            patch.object(watchdog, "CAMINHO_PC", Path("/tmp/saves")),
            patch.object(watchdog, "CAMINHO_BACKUP", Path("/tmp/backup")),
            patch.object(watchdog, "celular_conectado", return_value=True),
            patch.object(watchdog, "tempo_pc", side_effect=[1, 2]),
            patch.object(watchdog, "realizar_backup") as realizar_backup,
            patch.object(watchdog.time, "sleep", side_effect=KeyboardInterrupt),
            patch.object(watchdog.os, "system"),
            patch.object(watchdog.typer, "echo"),
        ):
            with self.assertRaises(KeyboardInterrupt):
                watchdog.vigiar_alteracoes()

            realizar_backup.assert_called_once_with(
                Path("/tmp/saves"),
                Path("/tmp/backup"),
                Path("/tmp/saves"),
            )

    def test_vigiar_alteracoes_pushes_after_backup(self):
        caminho_pc = Path("/tmp/saves")

        with (
            patch.object(watchdog, "CAMINHO_PC", caminho_pc),
            patch.object(watchdog, "CAMINHO_BACKUP", Path("/tmp/backup")),
            patch.object(watchdog, "CAMINHO_CELULAR", "/android/saves"),
            patch.object(watchdog, "celular_conectado", return_value=True),
            patch.object(watchdog, "tempo_pc", side_effect=[1, 2]),
            patch.object(watchdog, "realizar_backup"),
            patch.object(watchdog.time, "sleep", side_effect=KeyboardInterrupt),
            patch.object(watchdog.os, "system") as system,
            patch.object(watchdog.typer, "echo"),
        ):
            with self.assertRaises(KeyboardInterrupt):
                watchdog.vigiar_alteracoes()

            system.assert_called_once_with(f'adb push "{caminho_pc}/." "/android/saves"')

    def test_vigiar_alteracoes_does_not_sync_when_timestamp_is_unchanged(self):
        with (
            patch.object(watchdog, "CAMINHO_PC", Path("/tmp/saves")),
            patch.object(watchdog, "CAMINHO_BACKUP", Path("/tmp/backup")),
            patch.object(watchdog, "celular_conectado", return_value=True),
            patch.object(watchdog, "tempo_pc", side_effect=[2, 2]),
            patch.object(watchdog, "realizar_backup") as realizar_backup,
            patch.object(watchdog.time, "sleep", side_effect=KeyboardInterrupt),
            patch.object(watchdog.os, "system") as system,
            patch.object(watchdog.typer, "echo"),
        ):
            with self.assertRaises(KeyboardInterrupt):
                watchdog.vigiar_alteracoes()

            realizar_backup.assert_not_called()
            system.assert_not_called()
