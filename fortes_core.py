import os
import time
import datetime
import traceback
import win32api
import win32con
import win32gui
import pyautogui
from pyvda import VirtualDesktop, get_virtual_desktops

# ==============================================================================
# 1. GERENCIAMENTO DE LOGS
# ==============================================================================
class Logger:
    """Centraliza a gravação e exibição de logs do sistema."""
    
    def __init__(self, pasta_log: str = r"C:\TEMPORÁRIOS\OUTROS", nome_arquivo: str = "log_execucao.txt"):
        self.pasta_log = pasta_log
        self.caminho_log = os.path.join(pasta_log, nome_arquivo)
        os.makedirs(self.pasta_log, exist_ok=True)

    def registrar(self, mensagem: str, erro: Exception = None):
        data_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detalhe_erro = f"\n{traceback.format_exc()}" if erro else ""
        texto = f"[{data_hora}] {mensagem}{detalhe_erro}\n"
        
        print(f"ℹ️ {texto.strip()}")
        with open(self.caminho_log, "a", encoding="utf-8") as f:
            f.write(texto)


# ==============================================================================
# 2. GERENCIAMENTO DE JANELAS (WIN32 UNIFICADO)
# ==============================================================================
class WindowManager:
    """Agrupa utilitários para busca, foco e manipulação de janelas."""

    @staticmethod
    def buscar_janela_por_titulo(termo_busca: str):
        """Retorna (hwnd, titulo) da primeira janela visível que contenha o termo."""
        resultado = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo and termo_busca.lower() in titulo.lower():
                    resultado.append((hwnd, titulo))
            return True
        win32gui.EnumWindows(callback, None)
        return resultado[0] if resultado else None

    @staticmethod
    def focar_e_restaurar(hwnd):
        """Restaura e traz uma janela para o primeiro plano."""
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)

    @staticmethod
    def aguardar_janela(termo_busca: str, timeout: int = 120):
        """Aguarda a janela aparecer dentro do tempo limite especificado em segundos."""
        tempo_inicio = time.time()
        while (time.time() - tempo_inicio) < timeout:
            janela = WindowManager.buscar_janela_por_titulo(termo_busca)
            if janela:
                return janela
            time.sleep(1)
        return None


# ==============================================================================
# 3. GERENCIAMENTO DE ÁREAS VIRTUAIS (VIRTUAL DESKTOPS)
# ==============================================================================
class DesktopManager:
    """Gerencia a criação e alternância de áreas de trabalho virtuais."""

    @staticmethod
    def preparar_terceira_area(logger: Logger = None):
        try:
            total_desktops = len(get_virtual_desktops())
            if total_desktops >= 3:
                while len(get_virtual_desktops()) >= 3:
                    ultimo_indice = len(get_virtual_desktops())
                    VirtualDesktop(ultimo_indice).remove()
                    time.sleep(0.2)

            while len(get_virtual_desktops()) < 3:
                VirtualDesktop.create()
                time.sleep(0.2)

            VirtualDesktop(3).go()
            if logger:
                logger.registrar("3ª área de trabalho pronta e focada.")
        except Exception as e:
            if logger:
                logger.registrar("Erro ao gerenciar áreas virtuais", e)


# ==============================================================================
# 4. AUTOMAÇÃO DE AÇÕES DO FORTES AC
# ==============================================================================
class FortesAutomator:
    """Classe com as ações específicas do Fortes AC."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def realizar_logon(self, hwnd_logon, usuario: str = "ROBOCONT", senha: str = "123"):
        """Localiza os campos de texto do logon via Win32 e envia as credenciais + F9."""
        try:
            edits = []

            def callback_edits(hwnd, extra):
                if win32gui.GetClassName(hwnd) == "TDLEdit":
                    rect = win32gui.GetWindowRect(hwnd)
                    edits.append((hwnd, rect[1]))  # Salva HWND e Posição Y
                return True

            win32gui.EnumChildWindows(hwnd_logon, callback_edits, None)
            edits.sort(key=lambda item: item[1])  # Ordena do topo para o fundo

            if len(edits) < 2:
                raise Exception(f"Campos de logon não encontrados (Apenas {len(edits)} localizado).")

            hwnd_usuario, hwnd_senha = edits[0][0], edits[1][0]

            # Preenchimento direto via mensagem Win32
            win32gui.SendMessage(hwnd_usuario, win32con.WM_SETTEXT, 0, str(usuario))
            win32gui.SendMessage(hwnd_senha, win32con.WM_SETTEXT, 0, str(senha))
            time.sleep(0.5)

            WindowManager.focar_e_restaurar(hwnd_logon)

            # Envia tecla F9
            win32api.keybd_event(win32con.VK_F9, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_F9, 0, win32con.KEYEVENTF_KEYUP, 0)

            self.logger.registrar("Logon preenchido e confirmado com F9.")
        except Exception as e:
            self.logger.registrar("Erro durante a rotina de logon", e)

    def preencher_balancete(self, data_inicio: str = '01012025', data_fim: str = '31122025', opcao: str = '1'):
        """Executa o preenchimento da janela de Balancete."""
        time.sleep(0.5)
        pyautogui.press('tab', presses=2, interval=0.1)
        pyautogui.write(data_inicio, interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.write(data_fim, interval=0.05)
        pyautogui.press('tab', presses=4, interval=0.1)
        pyautogui.write(opcao, interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.press('enter')
        self.logger.registrar("Dados do Balancete preenchidos com sucesso.")