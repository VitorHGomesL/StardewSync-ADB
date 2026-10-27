import os
import shutil
from pathlib import Path
import platform
import typer
import json


# Caminho absoluto para a pasta de saves no sistema Android (via ADB)
CAMINHO_CELULAR = "/sdcard/Android/data/com.chucklefish.stardewvalley/files/Saves"
CONFIG_FILE = Path("caminhos.json")

def json_write(caminho_final: Path, caminho_backup: Path):
    """
    Registra os caminhos de salvamento do PC e do backup em um arquivo JSON."""
    Data =  {
        "caminho_pc": str(caminho_final),
        "caminho_backup": str(caminho_backup)
    }
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(Data, file, indent=4, ensure_ascii=False)


def json_read() -> tuple[Path | None, Path | None]:
    """
    Lê os caminhos de salvamento do PC e do backup a partir de um arquivo JSON.
    Retorna uma tupla contendo os caminhos absolutos.
    """
    """
    Lê os caminhos do arquivo JSON.
    Se não existir ou estiver vazio, retorna None.
    """
    if not CONFIG_FILE.exists():
        return None, None

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        caminho_pc_raw = data.get("caminho_pc", "")
        caminho_backup_raw = data.get("caminho_backup", "")

        if not isinstance(caminho_pc_raw, str):
            caminho_pc_raw = ""

        if not isinstance(caminho_backup_raw, str):
            caminho_backup_raw = ""

        caminho_pc_raw = caminho_pc_raw.strip()
        caminho_backup_raw = caminho_backup_raw.strip()

        caminho_pc = Path(caminho_pc_raw).expanduser().resolve() if caminho_pc_raw else None
        caminho_backup = Path(caminho_backup_raw).expanduser().resolve() if caminho_backup_raw else None

        return caminho_pc, caminho_backup

    except json.JSONDecodeError:
        return None, None

        
def configurar_caminhos():
    """
    Configura os caminhos de salvamento do PC e do backup.
    """
    typer.echo("\n---- Bem vindo ao Menu de Configuração do StardewSyncADB! ----\n")
    sistema = platform.system()

    # Seleção automática baseada no sistema operacional
    if sistema == "Windows":
        caminho_saves = Path(os.path.expandvars(r"%AppData%/StardewValley/Saves"))

    elif sistema == "Darwin":  # macOS
        caminho_saves = Path.home() / "Library/Application Support/StardewValley/Saves"

    elif sistema == "Linux":
        caminho_saves = Path.home() / ".config/StardewValley/Saves"

    else:
        raise OSError(f"Sistema operacional não suportado: {sistema}")

    # Fim da seleção automática baseada no sistema operacional

    if not caminho_saves.exists():
        caminho_manual = Path(
            input(
                f"Caminho Padrão '{caminho_saves}' não encontrado, por favor, insira o caminho manualmente:\n"
            ).strip()
        ).expanduser().resolve()

        if not caminho_manual.exists():
            raise FileNotFoundError(f"Caminho inválido: {caminho_manual}")

        if not caminho_manual.is_dir():
            raise NotADirectoryError(f"Caminho não é um diretório: {caminho_manual}")

        caminho_saves = caminho_manual

    else:
        typer.echo(
            f"\nDetectado o uso do sistema operacional {sistema}, "
            f"usado o caminho {caminho_saves} como Diretório padrão do jogo.\n"
        )

        aprovacao = input("Deseja prosseguir com o diretório acima? S/n: ").strip().lower()

        if aprovacao == "n":
            caminho_manual = Path(
                input("Por favor, insira o diretório do jogo: ").strip()
            ).expanduser().resolve()

            if not caminho_manual.exists():
                raise FileNotFoundError(f"Caminho inválido: {caminho_manual}")

            if not caminho_manual.is_dir():
                raise NotADirectoryError(f"Caminho não é um diretório: {caminho_manual}")

            caminho_saves = caminho_manual

        elif aprovacao not in ("", "s"):
            raise ValueError("Insira uma opção válida")

    caminho_backup = input('''
Por favor, insira o caminho de backup:
(Caso queira usar o caminho padrão, pressione enter e será criado uma pasta no diretório do programa em ./backups)
''').strip()

    if caminho_backup == "":
        caminho_backup = Path("./backups").expanduser().resolve()
    else:
        caminho_backup = Path(caminho_backup).expanduser().resolve()

    caminho_backup.mkdir(parents=True, exist_ok=True)

    json_write(caminho_saves, caminho_backup)

    typer.echo(
        f"Caminho do PC selecionado: {caminho_saves} | "
        f"Caminho de Backup selecionado: {caminho_backup}"
    )
