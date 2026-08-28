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
# BLOCO 0: UTILITÁRIOS E INFRAESTRUTURA (MICROFUNÇÕES E LOGS)
# ==============================================================================

def pausa_curta(segundos: float = 0.5) -> None:
    """Microfunção para pequenas pausas de estabilização da interface."""
    time.sleep(segundos)


def esperar_tela(termo_busca: str, timeout: int = 60, intervalo: float = 0.5):
    """
    Microfunção padronizada de espera de janelas.
    Tempo limite padrão: 1 minuto (60 segundos).
    """
    tempo_inicio = time.time()
    while (time.time() - tempo_inicio) < timeout:
        janela = WindowManager.buscar_janela_por_titulo(termo_busca)
        if janela:
            return janela
        time.sleep(intervalo)
    return None


class Logger:
    """Centraliza o registro de mensagens de execução e erros em arquivo TXT."""
    
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


class WindowManager:
    """Gerencia a busca e alteração de estado das janelas do Windows via Win32."""

    @staticmethod
    def buscar_janela_por_titulo(termo_busca: str):
        """Busca qualquer janela visível que contenha o termo informado."""
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
        """Restaura a janela se estiver minimizada e traz para o primeiro plano."""
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        pausa_curta(0.5)


# ==============================================================================
# PASSO 1: PREPARAÇÃO DO AMBIENTE (ÁREA VIRTUAL)
# ==============================================================================

class DesktopManager:
    """Prepara a Área de Trabalho Virtual limpa para a execução do robô."""

    @staticmethod
    def preparar_terceira_area(logger: Logger = None):
        try:
            total_desktops = len(get_virtual_desktops())
            if total_desktops >= 3:
                while len(get_virtual_desktops()) >= 3:
                    ultimo_indice = len(get_virtual_desktops())
                    VirtualDesktop(ultimo_indice).remove()
                    pausa_curta(0.2)

            while len(get_virtual_desktops()) < 3:
                VirtualDesktop.create()
                pausa_curta(0.2)

            VirtualDesktop(3).go()
            if logger:
                logger.registrar("Passo 1: 3ª área de trabalho pronta e focada.")
        except Exception as e:
            if logger:
                logger.registrar("Erro ao gerenciar áreas virtuais", e)


# ==============================================================================
# CLASSE PRINCIPAL: AUTOMAÇÃO DO FORTES AC (ORDEM CRONOLÓGICA)
# ==============================================================================

class FortesAutomator:
    """Encapsula as ações do usuário no Fortes AC em ordem sequencial."""

    def __init__(self, logger: Logger):
        self.logger = logger

    # --------------------------------------------------------------------------
    # PASSO 2: AUTENTICAÇÃO E LOGON
    # --------------------------------------------------------------------------
    def realizar_logon(self, hwnd_logon, usuario: str = "ROBOCONT", senha: str = "123") -> bool:
        """Preenche o usuário e senha na tela inicial e envia a tecla F9."""
        try:
            edits = []

            def callback_edits(hwnd, extra):
                if win32gui.GetClassName(hwnd) == "TDLEdit":
                    rect = win32gui.GetWindowRect(hwnd)
                    edits.append((hwnd, rect[1]))
                return True

            win32gui.EnumChildWindows(hwnd_logon, callback_edits, None)
            edits.sort(key=lambda item: item[1])

            if len(edits) < 2:
                raise Exception(f"Campos de logon não encontrados ({len(edits)} localizado).")

            hwnd_usuario, hwnd_senha = edits[0][0], edits[1][0]

            win32gui.SendMessage(hwnd_usuario, win32con.WM_SETTEXT, 0, str(usuario))
            win32gui.SendMessage(hwnd_senha, win32con.WM_SETTEXT, 0, str(senha))
            pausa_curta(0.5)

            WindowManager.focar_e_restaurar(hwnd_logon)

            win32api.keybd_event(win32con.VK_F9, 0, 0, 0)
            pausa_curta(0.1)
            win32api.keybd_event(win32con.VK_F9, 0, win32con.KEYEVENTF_KEYUP, 0)

            self.logger.registrar("Passo 2: Logon preenchido e confirmado com F9.")
            return True
        except Exception as e:
            self.logger.registrar("Erro na rotina de logon", e)
            return False

    # --------------------------------------------------------------------------
    # PASSO 3: SELEÇÃO DE EMPRESA
    # --------------------------------------------------------------------------
    def _trocar_empresa_no_fortes(self, codigo_empresa: str | int) -> bool:
        """Executa o atalho Ctrl+E e digita o código numérico da empresa."""
        str_codigo = str(codigo_empresa).strip()

        if not str_codigo.isdigit():
            self.logger.registrar(f"❌ O código '{codigo_empresa}' deve conter apenas números.")
            return False

        janela_fortes = WindowManager.buscar_janela_por_titulo("Setor Contábil") or WindowManager.buscar_janela_por_titulo("Fortes")
        if not janela_fortes:
            self.logger.registrar("❌ Tela do Fortes AC não encontrada para trocar empresa.")
            return False

        hwnd_fortes, _ = janela_fortes
        WindowManager.focar_e_restaurar(hwnd_fortes)
        pausa_curta(0.5)

        pyautogui.hotkey('ctrl', 'e')

        janela_empresa = esperar_tela("Empresa")
        if not janela_empresa:
            self.logger.registrar("❌ Janela de seleção de 'Empresa' não abriu no tempo limite.")
            return False

        hwnd_empresa, _ = janela_empresa
        WindowManager.focar_e_restaurar(hwnd_empresa)
        pausa_curta(0.5)

        pyautogui.write(str_codigo, interval=0.05)
        pausa_curta(0.2)
        pyautogui.press('tab')
        pausa_curta(0.2)
        pyautogui.press('enter')
        pausa_curta(0.5)

        self.logger.registrar(f"Passo 3: Empresa {str_codigo} selecionada com sucesso.")
        return True

    def escolher_empresa(self, empresas: int | str | list | tuple = None) -> bool:
        """
        Gerencia a escolha de empresas aceitando input do usuário, valor único ou lista.
        """
        if empresas is None:
            self.logger.registrar("Aguardando entrada do usuário via terminal...")
            entrada = input("👉 Digite o número da empresa desejada: ").strip()
            return self._trocar_empresa_no_fortes(entrada)

        elif isinstance(empresas, (list, tuple)):
            self.logger.registrar(f"Iniciando seleção em lote para {len(empresas)} empresa(s)...")
            sucesso_geral = True
            for emp in empresas:
                if not self._trocar_empresa_no_fortes(emp):
                    sucesso_geral = False
                pausa_curta(1.0)
            return sucesso_geral

        else:
            return self._trocar_empresa_no_fortes(empresas)

    # --------------------------------------------------------------------------
    # PASSO 4: PARAMETRIZAÇÃO DO BALANCETE
    # --------------------------------------------------------------------------
    def preencher_balancete(self, data_inicio: str = '01012025', data_fim: str = '31122025', opcao: str = '1'):
        """Preenche o período e o filtro da tela de Balancete."""
        pausa_curta(0.5)
        pyautogui.press('tab', presses=2, interval=0.1)
        pyautogui.write(data_inicio, interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.write(data_fim, interval=0.05)
        pyautogui.press('tab', presses=4, interval=0.1)
        pyautogui.write(opcao, interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.press('enter')
        self.logger.registrar("Passo 4: Parâmetros do Balancete preenchidos.")

    # --------------------------------------------------------------------------
    # PASSO 5: PRE-VISUALIZAÇÃO E EXPORTAÇÃO
    # --------------------------------------------------------------------------
    def gerar_balancete(self) -> bool:
        """Aguarda a pré-visualização do relatório, clica para exportar e salva o arquivo."""
        self.logger.registrar("Aguardando tela 'Pré-visualização' (tempo limite: 1 min)...")
        janela_preview = esperar_tela("Pré-visualização")

        if not janela_preview:
            self.logger.registrar("❌ Tela 'Pré-visualização' não encontrada.")
            return False

        hwnd_preview, _ = janela_preview
        WindowManager.focar_e_restaurar(hwnd_preview)
        pausa_curta(0.5)

        # Clique na coordenada de exportação
        pyautogui.click(x=93, y=78)
        self.logger.registrar("Clique na exportação (X=93, Y=78) realizado.")

        self.logger.registrar("Aguardando janela 'Salvar' (tempo limite: 1 min)...")
        janela_salvar = esperar_tela("Salvar")

        if not janela_salvar:
            self.logger.registrar("❌ Tela 'Salvar' não foi exibida.")
            return False

        hwnd_salvar, _ = janela_salvar
        WindowManager.focar_e_restaurar(hwnd_salvar)
        pausa_curta(0.5)

        # Sequência de comandos de salvamento
        pyautogui.press('tab')
        pausa_curta(0.1)
        pyautogui.hotkey('shift', 'tab')
        pausa_curta(0.1)
        pyautogui.press('d')
        pausa_curta(0.1)
        pyautogui.press('tab', presses=4, interval=0.1)
        pyautogui.press('enter')

        self.logger.registrar("Passo 5: Balancete gerado e salvo com sucesso.")
        return True