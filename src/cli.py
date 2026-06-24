from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from src.config import json_read
import platform
from pathlib import Path

CAMINHO_PC, CAMINHO_BACKUP = json_read()

console = Console()
sistema = platform.system()

def show_banner(caminho_pc, caminho_backup, android_conectado: bool):
    logo = Text()
    logo.append("STARDEW", style="bold #ffd43b")
    logo.append("SYNC", style="bold #7bd88f")
    logo.append("ADB", style="bold #5ec8ff")

    scene = Text.from_markup(
        """
[white]      ✦        .          ✦        .[/white]
[#1e90ff]  ─────────────────────────────[/#1e90ff]
[#7bdff2]        ☁        ☁        ☁[/#7bdff2]

[#2f9e44]       /\      /\        /\ [/#2f9e44]
[#2b8a3e]      /  \____/  \______/  \ [/#2b8a3e]
[#087f5b] ____/______________________\____[/#087f5b]

[#8d6e63]  ║═║═║═║═║═║═║═║═║═║═║═║[/#8d6e63]

[#b85c38]          ████████████[/#b85c38]
[#d9480f]         ██████████████[/#d9480f]
[#8d4925]        ██[/#8d4925][#c92a2a]██████████[/#c92a2a][#8d4925]██[/#8d4925]
[#6b4f3f]        ██  []  __  ██[/#6b4f3f]
[#6b4f3f]        ██      ||  ██[/#6b4f3f]
[#6b4f3f]        ██████████████[/#6b4f3f]

[#f08c00]             /\\_/\\ [/#f08c00]
[#f08c00]            ( o.o )[/#f08c00]
[#f08c00]             > ^ <[/#f08c00]

[#2f9e44]      ♧     ♧      ♧      ♧[/#2f9e44]
[#e67700]  ░░░░░░░░░░░░░░░░░░░░░░░░░[/#e67700]
"""
    )

    subtitle = Text("Bem vindo! ", style="bold white")
    sync = Text(f"{sistema}  ↔  Android", style="bold cyan")


    android_status = Text(
        "Android: CONECTADO" if android_conectado else "Android: DESCONECTADO",
        style="bold green" if android_conectado else "bold red"
    )

    pc_status = Text(
        f"Diretório PC: {caminho_pc}" if caminho_pc.exists() and caminho_pc != Path(" ") else "Diretório PC: NÃO ENCONTRADO",
        style="bold green" if caminho_pc.exists() and caminho_pc != Path(" ") else "bold red"
    )

    backup_status = Text(
        f"Backup: {caminho_backup}" if caminho_backup.exists() and caminho_backup != Path(" ") else "Backup: NÃO ENCONTRADO",
        style="bold green" if caminho_backup.exists() and caminho_backup != Path(" ") else "bold red"
    )

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
            border_style="green" if android_conectado else "red",
            padding=(1, 2),           
        )
    
    return Group(
        painel_logo,
        painel_status
    )