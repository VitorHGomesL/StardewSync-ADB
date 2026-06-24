import time

import typer
from src.config import json_read, configurar_caminhos
from src.watchdog import vigiar_alteracoes
from src.adb import sincronia_inicial, celular_conectado
from src.cli import show_banner
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
    CAMINHO_PC.mkdir(parents=True, exist_ok=True)
    CAMINHO_BACKUP.mkdir(parents=True, exist_ok=True)

    with Live(
        show_banner(caminho_pc, caminho_backup, android_conectado=False),
        refresh_per_second=4,
        screen=True
    ) as live:
        while True:
            conectado = celular_conectado()

            live.update(show_banner(caminho_pc, caminho_backup, android_conectado=conectado))
            time.sleep(2)



@app.command()
def versao():
    """
    Exibe a versão atual do programa.
    """
    typer.echo("StardewSync-ADB v0.5.0")

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