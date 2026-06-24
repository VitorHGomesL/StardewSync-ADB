import subprocess
import shutil
from pathlib import Path
import platform

from src.config import CAMINHO_CELULAR

def encontrar_adb() -> Path:
    adb_sistema = shutil.which("adb")
    if adb_sistema:
        return Path(adb_sistema)

    sistema = platform.system()

    if sistema == "Windows":
        adb_local = Path("platform-tools") / "adb.exe"
    else:
        adb_local = Path("platform-tools") / "adb"

    if adb_local.exists():
        return adb_local.resolve()

    raise FileNotFoundError(
        "ADB não encontrado. Instale o Android Platform Tools ou coloque a pasta platform-tools dentro do projeto."
    )


def adb_shell(*args: str) -> subprocess.CompletedProcess:
    adb = encontrar_adb()

    return subprocess.run(
        [str(adb), "shell", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def adb_pull(origem_android: str, destino_pc: Path) -> subprocess.CompletedProcess:
    adb = encontrar_adb()

    return subprocess.run(
        [str(adb), "pull", f"{origem_android}/.", str(destino_pc)],
        capture_output=True,
        text=True,
        check=True,
    )


def celular_conectado() -> bool:
    try:
        adb_shell("ls", CAMINHO_CELULAR)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def tempo_celular() -> float:
    try:
        resultado = adb_shell("stat", "-c", "%Y", CAMINHO_CELULAR)
        return float(resultado.stdout.strip())
    except FileNotFoundError:
        return 0
    except subprocess.CalledProcessError:
        return 0


def sincronia_inicial(caminho_pc: Path) -> str:
    from src.config import tempo_pc #noqa
    if not celular_conectado():
        return "Android desconectado"

    horario_celular = tempo_celular()
    horario_pc = tempo_pc(caminho_pc)

    if horario_celular > horario_pc:
        adb_pull(CAMINHO_CELULAR, caminho_pc)
        return "PC atualizado com o save do celular"

    if horario_pc > horario_celular:
        return "Save do PC é mais recente"

    return "Saves já estão sincronizados"