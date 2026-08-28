import os
import time
import datetime
import traceback
import win32api
import win32con
import win32gui
import pyautogui

# ==============================================================================
# BLOCO 0: UTILITÁRIOS E INFRAESTRUTURA (MICROFUNÇÕES E LOGS)
# ==============================================================================

def pausa_curta(segundos: float = 0.5) -> None:
    """Microfunção para pequenas pausas de estabilização da interface."""
    time.sleep(segundos)


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
    def buscar_janela_por_titulo(termo_busca: str | tuple | list):
        """
        Busca qualquer janela visível que contenha os termos informados,
        ignorando janelas do editor de código ou do terminal de comando.
        """
        if isinstance(termo_busca, str):
            termos = [termo_busca.lower()]
        else:
            termos = [t.lower() for t in termo_busca]

        # Evita identificar o próprio VS Code ou Terminal como a janela do Fortes
        titulos_ignorados = [".py", "visual studio code", "cmd.exe", "powershell", "windows powershell"]

        resultado = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo:
                    titulo_lower = titulo.lower()
                    
                    # Se for a janela do editor ou terminal, pula
                    if any(ignorar in titulo_lower for ignorar in titulos_ignorados):
                        return True

                    # Verifica se contém algum dos termos buscados
                    if any(termo in titulo_lower for termo in termos):
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


def esperar_tela(termo_busca: str | tuple | list, timeout: int = 60, intervalo: float = 0.5):
    """Aguarda o surgimento de uma janela dentro do tempo limite estipulado."""
    tempo_inicio = time.time()
    while (time.time() - tempo_inicio) < timeout:
        janela = WindowManager.buscar_janela_por_titulo(termo_busca)
        if janela:
            return janela
        time.sleep(intervalo)
    return None


# ==============================================================================
# PASSO 1: GERENCIAMENTO E ABERTURA DO FORTES AC
# ==============================================================================

def garantir_fortes_aberto(caminho_fortes: str, timeout: int = 120, logger: Logger = None):
    """
    Procura a janela do Fortes AC entre as janelas abertas no Windows.
    - Se encontrar: Restaura (caso minimizada) e traz para o foco.
    - Se não encontrar: Inicia o executável via atalho e aguarda a janela carregar.
    """
    # Termos específicos da aplicação Fortes AC
    termos_fortes = ("setor contábil", "fortes ac", "logon")

    # 1. Procura se a janela do sistema já está aberta
    janela_existente = WindowManager.buscar_janela_por_titulo(termos_fortes)
    if janela_existente:
        hwnd, titulo = janela_existente
        WindowManager.focar_e_restaurar(hwnd)
        if logger:
            logger.registrar(f"Fortes AC localizado ('{titulo}'). Janela restaurada e focada.")
        return janela_existente

    # 2. Se não encontrou a janela, executa o atalho do sistema
    if logger:
        logger.registrar("Janela do Fortes AC não encontrada. Executando o sistema...")
    
    os.startfile(caminho_fortes)

    # 3. Looping de espera até que a janela do sistema seja aberta
    janela_carregada = esperar_tela(termos_fortes, timeout=timeout)
    if janela_carregada:
        hwnd, titulo = janela_carregada
        WindowManager.focar_e_restaurar(hwnd)
        if logger:
            logger.registrar(f"Fortes AC detectado e pronto ('{titulo}').")
        return janela_carregada

    if logger:
        logger.registrar("❌ Limite de tempo excedido: A janela do Fortes AC não abriu.")
    return None


# ==============================================================================
# CLASSE PRINCIPAL: AUTOMAÇÃO DO FORTES AC (AÇÕES DE INTERFACE)
# ==============================================================================

class FortesAutomator:
    """Encapsula as interações com a interface do sistema Fortes AC."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def realizar_logon(self, hwnd_logon, usuario: str, senha: str) -> bool:
        """Preenche os campos de usuário/senha e envia F9."""
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

            self.logger.registrar(f"Passo 2: Logon do usuário '{usuario}' preenchido e confirmado.")
            return True
        except Exception as e:
            self.logger.registrar("Erro na rotina de logon", e)
            return False

    def _trocar_empresa_no_fortes(self, codigo_empresa: str | int) -> bool:
        """Executa o atalho Ctrl+E e envia o código numérico da empresa."""
        str_codigo = str(codigo_empresa).strip()

        if not str_codigo.isdigit():
            self.logger.registrar(f"❌ O código '{codigo_empresa}' deve conter apenas números.")
            return False

        janela_fortes = WindowManager.buscar_janela_por_titulo(("Setor Contábil", "Fortes AC"))
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
        """Gerencia a escolha de empresa por entrada direta, item único ou lista."""
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

    def preencher_balancete(self, data_inicio: str, data_fim: str, opcao: str):
        """Preenche o período do relatório e a opção de filtro."""
        pausa_curta(0.5)
        pyautogui.press('tab', presses=2, interval=0.1)
        pyautogui.write(str(data_inicio), interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.write(str(data_fim), interval=0.05)
        pyautogui.press('tab', presses=4, interval=0.1)
        pyautogui.write(str(opcao), interval=0.05)
        pyautogui.press('tab', interval=0.1)
        pyautogui.press('enter')
        self.logger.registrar(f"Passo 4: Balancete parametrizado ({data_inicio} a {data_fim}, Opção: {opcao}).")

    def gerar_balancete(
        self,
        caminho_pasta: str,
        nome_arquivo: str,
        pos_x: int = 93,
        pos_y: int = 78,
        letra_atalho: str = 'd',
        pos_btn_x: int = 1172,
        pos_btn_y: int = 454
    ) -> bool:
        """
        Aguarda a pré-visualização, seleciona a opção, abre a janela de destino
        e salva o arquivo no caminho e nome definidos.
        """
        self.logger.registrar("Aguardando tela 'Pré-visualização' (tempo limite: 1 min)...")
        janela_preview = esperar_tela("Pré-visualização")

        if not janela_preview:
            self.logger.registrar("❌ Tela 'Pré-visualização' não encontrada.")
            return False

        hwnd_preview, _ = janela_preview
        WindowManager.focar_e_restaurar(hwnd_preview)
        pausa_curta(0.5)

        pyautogui.click(x=pos_x, y=pos_y)
        self.logger.registrar(f"Clique na exportação (X={pos_x}, Y={pos_y}) realizado.")

        self.logger.registrar("Aguardando janela 'Salvar' (tempo limite: 1 min)...")
        janela_salvar = esperar_tela("Salvar")

        if not janela_salvar:
            self.logger.registrar("❌ Tela 'Salvar' não foi exibida.")
            return False

        hwnd_salvar, _ = janela_salvar
        WindowManager.focar_e_restaurar(hwnd_salvar)
        pausa_curta(0.5)

        pyautogui.press('tab')
        pausa_curta(0.1)
        pyautogui.hotkey('shift', 'tab')
        pausa_curta(0.1)
        pyautogui.press(str(letra_atalho))
        pausa_curta(0.1)
        pyautogui.press('tab')
        pausa_curta(0.2)

        pyautogui.click(x=pos_btn_x, y=pos_btn_y)
        self.logger.registrar(f"Clique no botão de caminho/arquivo (X={pos_btn_x}, Y={pos_btn_y}) realizado.")
        pausa_curta(0.8)

        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        os.makedirs(caminho_pasta, exist_ok=True)
        
        pyautogui.write(caminho_completo, interval=0.03)
        pausa_curta(0.3)

        pyautogui.press('tab', presses=3, interval=0.1)
        pausa_curta(0.2)
        pyautogui.press('enter')

        self.logger.registrar(f"Passo 5: Balancete gerado e salvo em '{caminho_completo}'.")
        return True