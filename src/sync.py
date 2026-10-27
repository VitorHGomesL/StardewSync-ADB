from pathlib import Path

from src.adb import adb_pull, adb_push, diagnosticar_android, tempo_celular
from src.backup import realizar_backup, tempo_pc
from src.config import CAMINHO_CELULAR


def sincronizar_manual(caminho_pc: Path | None, caminho_backup: Path | None) -> str:
    if (
        caminho_pc is None
        or caminho_backup is None
        or not caminho_pc.exists()
        or not caminho_pc.is_dir()
        or not caminho_backup.exists()
        or not caminho_backup.is_dir()
    ):
        return "Caminho do PC/Backup não configurado.\nUse: python3 main.py config"

    android_conectado, mensagem_android = diagnosticar_android()
    if not android_conectado:
        if mensagem_android == "Nenhum dispositivo ADB conectado":
            return "Android desconectado.\nConecte o celular via USB com depuração ativada."

        return f"{mensagem_android}.\nConecte o celular via USB com depuração ativada."

    horario_pc = tempo_pc(caminho_pc)
    horario_android = tempo_celular()

    if horario_pc == 0 and horario_android == 0:
        return "Não foi possível comparar os saves.\nVerifique os caminhos do PC e do Android."

    if horario_pc == horario_android:
        return "Saves já estão sincronizados.\nNada foi alterado."

    if horario_android > horario_pc:
        try:
            backup_criado = realizar_backup(CAMINHO_CELULAR, caminho_backup, caminho_pc)
        except Exception as erro:
            return f"Falha ao criar backup.\nSincronização cancelada.\nErro: {erro}"

        if not backup_criado:
            return "Falha ao criar backup.\nSincronização cancelada."

        try:
            adb_pull(CAMINHO_CELULAR, caminho_pc)
        except Exception as erro:
            return f"Falha ao puxar save do Android.\nBackup foi mantido.\nErro: {erro}"

        return "Android conectado.\nBackup criado.\nAndroid mais recente.\nSave puxado para o PC."

    try:
        backup_criado = realizar_backup(caminho_pc, caminho_backup, caminho_pc)
    except Exception as erro:
        return f"Falha ao criar backup.\nSincronização cancelada.\nErro: {erro}"

    if not backup_criado:
        return "Falha ao criar backup.\nSincronização cancelada."

    try:
        adb_push(caminho_pc, CAMINHO_CELULAR)
    except Exception as erro:
        return f"Falha ao enviar save para o Android.\nBackup foi mantido.\nErro: {erro}"

    return "Android conectado.\nBackup criado.\nPC mais recente.\nSave enviado para o Android."
