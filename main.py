import time
from src.config import CAMINHO_PC, CAMINHO_BACKUP
from src.connections import celular_conectado
from src.watchdog import sincronia_inicial, vigiar_alteracoes

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

if __name__ == "__main__":
    main()