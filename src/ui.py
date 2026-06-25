from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from src.adb import celular_conectado
import platform
from pathlib import Path


console = Console()
sistema = platform.system()

def caminho_configurado(caminho: Path) -> bool:
    return str(caminho).strip() != "" and caminho.exists() and caminho.is_dir()


def status_atual(caminho_pc, caminho_backup):
    if caminho_pc is None or caminho_backup is None:
        return "Caminho do PC/Backup não configurado. Use o comando configurar e reinicie."

    status_pc = caminho_pc.exists() and caminho_pc.is_dir()
    status_backup = caminho_backup.exists() and caminho_backup.is_dir()

    if not status_pc or not status_backup:
        return "Caminho do PC/Backup não configurado. Use o comando configurar e reinicie."

    if not celular_conectado():
        return "Celular desconectado. Conecte o Android via USB com depuração ativada."

    return "Serviço em funcionamento!"

def show_banner(
        caminho_pc,
        caminho_backup,
        status_texto,
        tela, 
        android_conectado: bool, 
        android_status_texto="Inicializando diagnóstico Android..."):
    logo = Text()
    logo.append("STARDEW", style="bold #ffd43b")
    logo.append("SYNC", style="bold #7bd88f")
    logo.append("ADB", style="bold #5ec8ff")

    scene = Text.from_markup(tela)


    subtitle = Text("Bem vindo! ", style="bold white")
    sync = Text(f"{sistema}  ↔  Android", style="bold cyan")


    android_status = Text(
    f"Android: {android_status_texto}",
    style="bold green" if android_conectado else "bold red"
    )

    if caminho_pc is None:
        pc_status = Text("Diretório PC: NÃO CONFIGURADO", style="bold red")
    elif caminho_pc.exists() and caminho_pc.is_dir():
        pc_status = Text(f"Diretório PC: {caminho_pc}", style="bold green")
    else:
        pc_status = Text("Diretório PC: NÃO ENCONTRADO", style="bold red")

    if caminho_backup is None:
        backup_status = Text("Backup: NÃO CONFIGURADO", style="bold red")
    elif caminho_backup.exists() and caminho_backup.is_dir():
        backup_status = Text(f"Backup: {caminho_backup}", style="bold green")
    else:
        backup_status = Text("Backup: NÃO ENCONTRADO", style="bold red")

    content = Group(
        Align.center(logo),
        Align.center(scene),
        Align.center(subtitle),
        Align.center(sync),

    )

    status = Group(
        Align.center(android_status),
        Align.center(pc_status),
        Align.center(backup_status)        
    )

    painel_logo =  Panel(
            content,
            title="[bold green]🌱 StardewSyncADB[/bold green]",
            subtitle=f"[dim]v1.5.0[/dim]",
            border_style="yellow",
            padding=(1, 2),
        )

    painel_status = Panel(
            status,
            title="[bold green]Status[/bold green]",
            subtitle=f"[bold white]Status Atual: {status_texto}[/bold white]" ,
            border_style="green" if android_conectado else "red",
            padding=(1, 2),           
        )
    
    return Group(
        painel_logo,
        painel_status
    )