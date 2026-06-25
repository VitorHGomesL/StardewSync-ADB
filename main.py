import time

import typer
from src.config import json_read, configurar_caminhos
from src.watchdog import vigiar_alteracoes
from src.adb import sincronia_inicial, celular_conectado
from src.cli import show_banner, status_atual
from rich.live import Live
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

    with Live(
        show_banner(caminho_pc, caminho_backup, status_texto, android_conectado=False),
        refresh_per_second=4,
        screen=True
    ) as live:
        while True:
            conectado = celular_conectado()

            if caminho_pc is None or caminho_backup is None:
                status_texto = "Caminho do PC/Backup não configurado"
            else:
                status_texto = status_atual(caminho_pc, caminho_backup)
                
            live.update(show_banner(caminho_pc, caminho_backup, status_texto, android_conectado=conectado))
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

if __name__ == "__main__":
    app()