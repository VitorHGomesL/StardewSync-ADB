import os
import shutil
from pathlib import Path
import platform
import typer
import json
from  src.config import CAMINHO_CELULAR

def realizar_backup(origem_padrao, caminho_backup, caminho_pc):
    """
    Avalia a versão mais recente dos dados entre PC, Android e o último Backup.
    Garante que a versão mais atual seja protegida no diretório de segurança
    antes de qualquer substituição (Fail-safe).
    """
    from src.adb import tempo_celular#noqa
    origem = None
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
