import unittest
from pathlib import Path
from unittest.mock import patch

import src.watchdog as watchdog


class TestWatchdog(unittest.TestCase):
    def test_vigiar_alteracoes_uses_current_function_signatures(self):
        with (
            patch.object(watchdog, "CAMINHO_PC", Path("/tmp/saves")),
            patch.object(watchdog, "CAMINHO_BACKUP", Path("/tmp/backup")),
            patch.object(watchdog, "celular_conectado", return_value=True),
            patch.object(watchdog, "tempo_pc", side_effect=[1, 2]),
            patch.object(watchdog, "realizar_backup") as realizar_backup,
            patch.object(watchdog.time, "sleep", side_effect=KeyboardInterrupt),
            patch.object(watchdog.os, "system"),
        ):
            with self.assertRaises(KeyboardInterrupt):
                watchdog.vigiar_alteracoes()

            realizar_backup.assert_called_once_with(
                Path("/tmp/saves"),
                Path("/tmp/backup"),
                Path("/tmp/saves"),
            )
