import time
import typer
from src.config import json_read, configurar_caminhos
from src.adb import celular_conectado, diagnosticar_android
from src.sync import sincronizar_manual
from src.ui import show_banner, status_atual
from rich.live import Live
from src.cli import TELA_GATO_PISCANDO
app = typer.Typer()

CAMINHO_PC, CAMINHO_BACKUP = json_read()

@app.command()
def iniciar():
    """
    Inicia o programa.
    """
    caminho_pc, caminho_backup = json_read()
    # Prepara o ambiente estrutural. Ignora (exist_ok) se as pastas já existirem
    status_texto = "Inicializando..."
    tela_indice = 0

    with Live(
        show_banner(
            caminho_pc,
            caminho_backup,
            status_texto,
            tela=TELA_GATO_PISCANDO[tela_indice],
            android_conectado=False,
            android_status_texto="Inicializando diagnóstico Android...",
        ),
        refresh_per_second=4,
        screen=True,
    ) as live:
        while True:
            conectado, mensagem_android = diagnosticar_android()

            tela_indice = (tela_indice + 1) % len(TELA_GATO_PISCANDO)

            if caminho_pc is None or caminho_backup is None:
                status_texto = "Caminho do PC/Backup não configurado"
            else:
                status_texto = status_atual(caminho_pc, caminho_backup)

            live.update(
                show_banner(
                    caminho_pc,
                    caminho_backup,
                    status_texto,
                    tela=TELA_GATO_PISCANDO[tela_indice],
                    android_conectado=conectado,
                    android_status_texto=mensagem_android,
                )
            )

            time.sleep(2)

@app.command()
def caminhos():
    """
    Exibe os caminhos de configuração atuais.
    """
    typer.echo(f"Caminho do PC: {CAMINHO_PC}")
    typer.echo(f"Caminho do Backup: {CAMINHO_BACKUP}")

@app.command()
def config():
    """
    Configura os caminhos do jogo e do backup
    """
    configurar_caminhos()

@app.command()
def sincronizar():
    """
    Sincroniza manualmente o save mais recente entre PC e Android.
    """
    caminho_pc, caminho_backup = json_read()
    typer.echo(sincronizar_manual(caminho_pc, caminho_backup))

if __name__ == "__main__":
    app()
