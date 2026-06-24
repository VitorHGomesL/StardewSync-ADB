import os
import shutil
import subprocess
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
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {CONFIG_FILE}")
    try:
        with CONFIG_FILE.open("r", encoding ="utf-8") as file:
            data = json.load(file)

        return Path(data["caminho_pc"]), Path(data["caminho_backup"])
    except json.JSONDecodeError:
        raise ValueError(f"Erro ao ler o arquivo de configuração")
    
    except KeyError as e:
        raise KeyError(f"Chave ausente no arquivo de configuração: {e}")

        
def configurar_caminhos() -> tuple[Path, Path]:
    """
    Configura os caminhos de salvamento do PC e do backup.
    Retorna uma tupla contendo os caminhos absolutos.
    """
    sistema = platform.system()

    if sistema == "Windows":
        caminho_final = Path(os.path.expandvars(r"%AppData%/StardewValley/Saves"))

    elif sistema == "Darwin":  # macOS
        caminho_final = Path.home() / "Library/Application Support/StardewValley/Saves"

    elif sistema == "Linux":
        caminho_final = Path.home() / ".config/StardewValley/Saves"

    if not caminho_final.is_dir():
        raise FileNotFoundError(f"Caminho inválido: {caminho_final}")
    if not caminho_final.exists():
        return f"Caminho: '{caminho_final}' não encontrado"
        caminho_manual = Path(input("Por favor, insira o diretório do jogo: ").strip()).expanduser().resolve()
        if not caminho_manual.exists() or not caminho_manual.is_dir():
            raise FileNotFoundError(f"Caminho inválido: {caminho_manual}")
        if not caminho_manual.is_dir():
            raise NotADirectoryError(f"Caminho não é um diretório: {caminho_manual}")
        caminho_final = caminho_manual

    caminho_backup = Path(input("Por favor, insira o caminho de backup: ").strip()).expanduser().resolve()


    json_write(caminho_final, caminho_backup)

    return f"Caminho do PC selecionado: {caminho_final} | Caminho de Backup selecionado: {caminho_backup}"

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
    
    # Define o timestamp da pasta raiz como ponto de partida
    tempo_mais_novo = caminho_pc.stat().st_mtime
    
    # O rglob('*') varre todos os arquivos internos e subdiretórios
    for item in caminho_pc.rglob('*'):
        if item.stat().st_mtime > tempo_mais_novo:
            tempo_mais_novo = item.stat().st_mtime
            
    return tempo_mais_novo
