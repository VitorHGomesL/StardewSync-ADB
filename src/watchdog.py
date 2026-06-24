import os
import time
import subprocess
import typer
from datetime import datetime
from src.config import CAMINHO_CELULAR, json_read, tempo_pc, realizar_backup
from src.adb import celular_conectado, tempo_celular
   
CAMINHO_PC, CAMINHO_BACKUP = json_read()

def vigiar_alteracoes():
    """
    Inicia o loop contínuo de observação de arquivos do PC enquanto o jogo está aberto.
    Ao detectar um novo salvamento (evento de alteração de arquivo), aciona
    a criação do backup de segurança e atualiza o Android automaticamente (Push).
    """
    typer.echo("Monitorando jogo... Não desconecte o celular.")
    
    # Define a referência temporal inicial (Snapshot base)
    horario_visto = tempo_pc()
    
    while True:
        try:
            # Validação contínua da conexão física para evitar travamentos silenciosos
            if not celular_conectado():
                typer.echo("Conexão com o celular perdida!")
                break

            # Snapshot temporal do ciclo atual
            tempo_atual = tempo_pc()
            
            # Condição de gatilho: Alteração detectada no diretório
            if tempo_atual > horario_visto:
                typer.echo(f"[{datetime.now().strftime('%H:%M:%S')}] Save detectado! Sincronizando...")
                
                realizar_backup(CAMINHO_PC)
                os.system(f'adb push "{CAMINHO_PC}/." "{CAMINHO_CELULAR}"')
                
                # Atualiza a referência temporal para aguardar o próximo save
                horario_visto = tempo_atual 
                
            # Intervalo de processamento (reduz o consumo de CPU da thread)
            time.sleep(2) 
            
        except Exception as e:
            # Captura erros não previstos e quebra o loop com segurança
            typer.echo(f"Erro na vigília (celular desplugado?): {e}")
            break
