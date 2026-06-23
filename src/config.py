import os
import shutil
import subprocess
from pathlib import Path

# Caminho absoluto para a pasta de saves no sistema Android (via ADB)
CAMINHO_CELULAR = "/sdcard/Android/data/com.chucklefish.stardewvalley/files/Saves"
# Caminho dinâmico para a pasta de saves no PC (resolve a variável %AppData% do sistema)
CAMINHO_PC = Path(os.path.expandvars(r"%AppData%\StardewValley\Saves"))
# Diretório local destinado ao armazenamento de cópias de segurança
CAMINHO_BACKUP = Path("SAVES_TESTS")

def realizar_backup(origem_padrao):
    """
    Avalia a versão mais recente dos dados entre PC, Android e o último Backup.
    Garante que a versão mais atual seja protegida no diretório de segurança
    antes de qualquer substituição (Fail-safe).
    """
    origem = origem_padrao
    horario_celular = tempo_celular()
    horario_pc = tempo_pc()
    
    # Validação estrutural do diretório de backup
    if CAMINHO_BACKUP.exists():
        horario_backup = CAMINHO_BACKUP.stat().st_mtime
    else:
        horario_backup = 0

    # Lógica de decisão de estado do backup
    if horario_pc > horario_backup and horario_pc > horario_celular:
        origem = CAMINHO_PC
    elif horario_celular > horario_backup and horario_celular > horario_pc:
        origem = CAMINHO_CELULAR
    
    # Execução baseada na origem selecionada
    if origem == CAMINHO_PC:
        shutil.copytree(CAMINHO_PC, CAMINHO_BACKUP, dirs_exist_ok=True)
    elif origem == CAMINHO_CELULAR:
        os.system(f'adb pull "{CAMINHO_CELULAR}/." "{CAMINHO_BACKUP}"')

def tempo_pc():
    """
    Realiza uma varredura profunda (Deep Scan) no diretório de saves do PC.
    Contorna a limitação do Windows, que não atualiza a data da pasta raiz 
    quando arquivos internos (subpastas de saves) são modificados.
    Retorna o timestamp (st_mtime) da alteração mais recente.
    """
    # Define o timestamp da pasta raiz como ponto de partida
    tempo_mais_novo = CAMINHO_PC.stat().st_mtime
    
    # O rglob('*') varre todos os arquivos internos e subdiretórios
    for item in CAMINHO_PC.rglob('*'):
        if item.stat().st_mtime > tempo_mais_novo:
            tempo_mais_novo = item.stat().st_mtime
            
    return tempo_mais_novo

def tempo_celular():
    """
    Consulta diretamente o kernel do Android (via shell do ADB) para obter 
    a data de modificação real da pasta de saves.
    Retorna o tempo em segundos (float) ou 0 caso o caminho não responda.
    """
    try:
        saida = subprocess.check_output(f'adb shell stat -c %Y "{CAMINHO_CELULAR}"', shell=True)
        return float(saida.strip())
    except:
        return 0