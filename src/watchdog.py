import os
import time
import subprocess
from datetime import datetime
from src.config import CAMINHO_CELULAR, CAMINHO_PC, CAMINHO_BACKUP, tempo_celular, tempo_pc, realizar_backup
from src.connections import celular_conectado

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
