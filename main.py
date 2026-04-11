import os
import shutil
import time
import subprocess
from pathlib import Path
from datetime import datetime

# ==========================================================
# 1. CONFIGURAÇÕES INICIAIS E MAPEAMENTO DE DIRETÓRIOS
# ==========================================================

# Caminho absoluto para a pasta de saves no sistema Android (via ADB)
CAMINHO_CELULAR = ("/sdcard/Android/data/com.chucklefish.stardewvalley/files/Saves")
# Caminho dinâmico para a pasta de saves no PC (resolve a variável %AppData% do sistema)
CAMINHO_PC = Path(os.path.expandvars(r"%AppData%\StardewValley\Saves"))
# Diretório local destinado ao armazenamento de cópias de segurança
CAMINHO_BACKUP = Path(r"SAVES_TESTS")

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

def celular_conectado():
    """
    Verifica a conectividade contínua com o dispositivo Android via protocolo ADB.
    Retorna True se o caminho do save for acessível, False em caso de desconexão.
    """
    try:
        # Redireciona o log de erro para o DEVNULL para manter o console limpo
        subprocess.check_output(f'adb shell ls "{CAMINHO_CELULAR}"', shell=True, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

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

# ==========================================================
# 2. FLUXO DE SINCRONIZAÇÃO E MONITORAMENTO (WATCHDOG)
# ==========================================================

def sincronia_inicial():
    """
    Rotina executada na primeira detecção de conexão validada.
    Compara as versões do save e atualiza o estado local (PC) caso 
    o usuário tenha jogado no dispositivo móvel recentemente.
    """
    print("Sincronizando save do Celular para o PC...")

    if celular_conectado():
        horario_celular = tempo_celular()
        horario_pc = tempo_pc()
        
        # Puxa os dados (pull) se o Android tiver a versão mais nova
        if horario_celular > horario_pc:    
            os.system(f'adb pull "{CAMINHO_CELULAR}/." "{CAMINHO_PC}"')
            print("Pc atualizado com o save do celular")
   

def vigiar_alteracoes():
    """
    Inicia o loop contínuo de observação de arquivos do PC enquanto o jogo está aberto.
    Ao detectar um novo salvamento (evento de alteração de arquivo), aciona
    a criação do backup de segurança e atualiza o Android automaticamente (Push).
    """
    print("Monitorando jogo... Não desconecte o celular.")
    
    # Define a referência temporal inicial (Snapshot base)
    horario_visto = tempo_pc()
    
    while True:
        try:
            # Validação contínua da conexão física para evitar travamentos silenciosos
            if not celular_conectado():
                print("Conexão com o celular perdida!")
                break

            # Snapshot temporal do ciclo atual
            tempo_atual = tempo_pc()
            
            # Condição de gatilho: Alteração detectada no diretório
            if tempo_atual > horario_visto:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Save detectado! Sincronizando...")
                
                realizar_backup(CAMINHO_PC)
                os.system(f'adb push "{CAMINHO_PC}/." "{CAMINHO_CELULAR}"')
                
                # Atualiza a referência temporal para aguardar o próximo save
                horario_visto = tempo_atual 
                
            # Intervalo de processamento (reduz o consumo de CPU da thread)
            time.sleep(2) 
            
        except Exception as e:
            # Captura erros não previstos e quebra o loop com segurança
            print(f"Erro na vigília (celular desplugado?): {e}")
            break

# ==========================================================
# 3. ENTRADA DE EXECUÇÃO (MAIN)
# ==========================================================

def main():
    # Prepara o ambiente estrutural. Ignora (exist_ok) se as pastas já existirem
    CAMINHO_PC.mkdir(parents=True, exist_ok=True)
    CAMINHO_BACKUP.mkdir(parents=True, exist_ok=True)
    
    print("=== STARDEW USB SYNC ATIVO ===")
    
    # Loop primário: Polling por detecção de dispositivo Android (ADB)
    while True:
        if celular_conectado():
            print("Celular encontrado!")
            
            # Gatilhos de regras de negócio
            sincronia_inicial()
            vigiar_alteracoes()
            
            # Retorno após quebra da vigília (ex: desconexão física)
            print("Sincronização encerrada. Aguardando nova conexão...")
        else:
            # Mantém o sistema em espera ativa otimizada
            print("Caminho não encontrado, tentando novamente...")
            time.sleep(2)
            pass

# Ponto de entrada padrão do Python
if __name__ == "__main__":
    main()