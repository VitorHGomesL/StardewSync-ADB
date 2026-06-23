import subprocess
from src.config import CAMINHO_CELULAR

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
    