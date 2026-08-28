import os
import time
from fortes_core import Logger, WindowManager, DesktopManager, FortesAutomator

def rodar_automacao():
    logger = Logger()
    automator = FortesAutomator(logger)

    # 1. Organizar Desktop
    DesktopManager.preparar_terceira_area(logger)

    # 2. Iniciar Sistema
    caminho_fortes = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Fortes AC"
    os.startfile(caminho_fortes)

    # 3. Aguardar e Realizar Logon
    janela_logon = WindowManager.aguardar_janela("logon", timeout=120)
    if janela_logon:
        hwnd_logon, _ = janela_logon
        automator.realizar_logon(hwnd_logon, usuario="ROBOCONT", senha="123")
    else:
        logger.registrar("Falha: Tela de logon não foi localizada no tempo limite.")

if __name__ == "__main__":
    rodar_automacao()