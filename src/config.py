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


def json_read() -> tuple[Path, Path]:
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

        caminho_pc_raw = data.get("caminho_pc", "").strip()
        caminho_backup_raw = data.get("caminho_backup", "").strip()

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

def realizar_backup(origem_padrao, caminho_backup, caminho_pc):
    """
    Avalia a versão mais recente dos dados entre PC, Android e o último Backup.
    Garante que a versão mais atual seja protegida no diretório de segurança
    antes de qualquer substituição (Fail-safe).
    """
    from src.adb import tempo_celular#noqa
    origem = origem_padrao
    horario_celular = tempo_celular()
    horario_pc = tempo_pc(caminho_pc)
    
    # Validação estrutural do diretório de backup
    if caminho_backup.exists():
        horario_backup = caminho_backup.stat().st_mtime
    else:
        horario_backup = 0

    # Lógica de decisão de estado do backup
    if horario_pc > horario_backup and horario_pc > horario_celular:
        origem = caminho_pc
    elif horario_celular > horario_backup and horario_celular > horario_pc:
        origem = CAMINHO_CELULAR
    
    # Execução baseada na origem selecionada
    if origem == caminho_pc:
        shutil.copytree(caminho_pc, caminho_backup, dirs_exist_ok=True)
    elif origem == CAMINHO_CELULAR:
        os.system(f'adb pull "{CAMINHO_CELULAR}/." "{caminho_backup}"')

def tempo_pc(caminho_pc):
    """
    Realiza uma varredura profunda (Deep Scan) no diretório de saves do PC.
    Contorna a limitação do Windows, que não atualiza a data da pasta raiz 
    quando arquivos internos (subpastas de saves) são modificados.
    Retorna o timestamp (st_mtime) da alteração mais recente.
    """

    if not caminho_pc.exists():
        typer.echo(f"Pasta de saves do PC não encontrada: {caminho_pc}")
        return 0

    tempo_mais_novo = caminho_pc.stat().st_mtime
    
    for item in caminho_pc.rglob('*'):
        if item.stat().st_mtime > tempo_mais_novo:
            tempo_mais_novo = item.stat().st_mtime
            
    return tempo_mais_novo
