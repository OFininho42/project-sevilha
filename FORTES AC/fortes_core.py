import os
import time
import datetime
import traceback
import win32api
import win32con
import win32gui
import pyautogui

# ==============================================================================
# ETAPA 1: INFRAESTRUTURA, REGISTRO E CAPTURA DE ERROS
# ==============================================================================

def pausa_curta(segundos: float = 0.5) -> None:
    """Microfunção para pausas naturais de estabilização da interface humana."""
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


def capturar_tela_erro(nome_acao: str = "erro_travamento", logger: Logger = None) -> str:
    r"""
    Tira um print da tela inteira quando o robô identifica uma tela inesperada
    e salva o arquivo PNG na pasta C:\TEMPORÁRIOS\OUTROS\ERROS DE EXECUCAO.
    """
    pasta_erros = r"C:\TEMPORÁRIOS\OUTROS\ERROS DE EXECUCAO"
    os.makedirs(pasta_erros, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"{nome_acao}_{timestamp}.png"
    caminho_completo = os.path.join(pasta_erros, nome_arquivo)
    
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(caminho_completo)
        if logger:
            logger.registrar(f"📸 Print de erro salvo em: {caminho_completo}")
        return caminho_completo
    except Exception as e:
        if logger:
            logger.registrar("❌ Falha ao gerar print de tela do erro.", e)
        return ""


# ==============================================================================
# ETAPA 2: GERENCIAMENTO E VALIDAÇÃO RIGOROSA DE JANELAS
# ==============================================================================

class WindowManager:
    """Gerencia a busca e alteração de estado das janelas do Windows via Win32."""

    @staticmethod
    def buscar_janela_por_titulo(termo_busca: str | tuple | list):
        """Busca janelas visíveis ignorando o próprio editor de código ou terminal."""
        if isinstance(termo_busca, str):
            termos = [termo_busca.lower()]
        else:
            termos = [t.lower() for t in termo_busca]

        titulos_ignorados = [".py", "visual studio code", "cmd.exe", "powershell", "windows powershell"]

        resultado = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo:
                    titulo_lower = titulo.lower()
                    if any(ignorar in titulo_lower for ignorar in titulos_ignorados):
                        return True
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


def esperar_tela(termo_esperado: str | tuple | list, timeout: int = 30, intervalo: float = 0.5, logger: Logger = None):
    """
    Aguarda exclusivamente pela tela esperada. 
    Se qualquer outra janela de alerta/aviso surgir ou o tempo esgotar, para imediatamente.
    """
    tempo_inicio = time.time()
    
    while (time.time() - tempo_inicio) < timeout:
        janela = WindowManager.buscar_janela_por_titulo(termo_esperado)
        if janela:
            return janela

        janela_alerta = WindowManager.buscar_janela_por_titulo(("atenção", "atencao", "erro", "aviso", "falha"))
        if janela_alerta:
            hwnd_alerta, titulo_alerta = janela_alerta
            if logger:
                logger.registrar(f"🛑 Parada obrigatória: Janela inesperada detectada ('{titulo_alerta}').")
            capturar_tela_erro(f"parada_inesperada_{titulo_alerta[:15]}", logger)
            return None

        time.sleep(intervalo)

    if logger:
        logger.registrar(f"❌ Tempo limite ({timeout}s) esgotado aguardando a tela: {termo_esperado}")
        capturar_tela_erro("timeout_aguardando_tela", logger)
        
    return None


# ==============================================================================
# ETAPA 3: ABERTURA E VERIFICAÇÃO DO SISTEMA
# ==============================================================================

def garantir_fortes_aberto(caminho_fortes: str, timeout: int = 30, logger: Logger = None):
    """Garante que a aplicação esteja aberta com limite de busca de 30 segundos."""
    termos_fortes = ("setor contábil", "fortes ac", "logon")

    janela_existente = WindowManager.buscar_janela_por_titulo(termos_fortes)
    if janela_existente:
        hwnd, titulo = janela_existente
        WindowManager.focar_e_restaurar(hwnd)
        if logger:
            logger.registrar(f"Fortes AC localizado ('{titulo}'). Janela restaurada.")
        pausa_curta(1.5)
        return janela_existente

    if logger:
        logger.registrar("Janela do Fortes AC não encontrada. Executando o sistema...")
    
    os.startfile(caminho_fortes)

    janela_carregada = esperar_tela(termos_fortes, timeout=timeout, logger=logger)
    if janela_carregada:
        hwnd, titulo = janela_carregada
        WindowManager.focar_e_restaurar(hwnd)
        if logger:
            logger.registrar(f"Fortes AC detectado ('{titulo}').")
        pausa_curta(1.5)
        return janela_carregada

    if logger:
        logger.registrar("❌ Limite de tempo (30s) excedido: A janela do Fortes AC não abriu.")
        capturar_tela_erro("abertura_fortes_falha", logger)
    return None


# ==============================================================================
# ETAPA 4: CLASSE PRINCIPAL DE AUTOMAÇÃO (FortesAutomator)
# ==============================================================================

class FortesAutomator:
    """Encapsula as interações na interface simulando cadência humana."""

    def __init__(self, logger: Logger = None):
        self.logger = logger or Logger()

    def escolher_empresa(self, empresas: str | int) -> bool:
        """Executa a troca de empresa simulando digitação humana calma."""
        str_codigo = str(empresas).strip()

        janela_fortes = WindowManager.buscar_janela_por_titulo(("Setor Contábil", "Fortes AC"))
        if not janela_fortes:
            self.logger.registrar("❌ Tela do Fortes AC não encontrada para trocar empresa.")
            capturar_tela_erro("empresa_tela_fortes_nao_encontrada", self.logger)
            return False

        hwnd_fortes, _ = janela_fortes
        WindowManager.focar_e_restaurar(hwnd_fortes)
        pausa_curta(0.5)

        pyautogui.hotkey('ctrl', 'e')

        janela_empresa = esperar_tela("Empresa", timeout=30, logger=self.logger)
        if not janela_empresa:
            self.logger.registrar("❌ Janela de seleção de 'Empresa' não abriu no tempo limite.")
            capturar_tela_erro("empresa_janela_nao_abriu", self.logger)
            return False

        hwnd_empresa, _ = janela_empresa
        WindowManager.focar_e_restaurar(hwnd_empresa)
        pausa_curta(0.6)

        pyautogui.write(str_codigo, interval=0.1)
        pausa_curta(0.4)
        pyautogui.press('tab')
        pausa_curta(0.3)
        pyautogui.press('enter')
        pausa_curta(1.0)

        self.logger.registrar(f"Empresa {str_codigo} selecionada com sucesso.")
        return True

    def preencher_balancete(self, data_inicio: str, data_fim: str, opcao: str):
        """Clica no menu do Balancete Contábil e preenche os parâmetros com cadência humana."""
        POS_BALANCETE_X = 359
        POS_BALANCETE_Y = 85

        self.logger.registrar(f"Clicando no menu Balancete (X={POS_BALANCETE_X}, Y={POS_BALANCETE_Y})...")
        pyautogui.click(x=POS_BALANCETE_X, y=POS_BALANCETE_Y)
        pausa_curta(1.0)

        pyautogui.press('tab', presses=2, interval=0.2)
        pausa_curta(0.3)
        pyautogui.write(str(data_inicio), interval=0.1)
        pausa_curta(0.3)
        
        pyautogui.press('tab', interval=0.2)
        pausa_curta(0.3)
        pyautogui.write(str(data_fim), interval=0.1)
        pausa_curta(0.3)
        
        pyautogui.press('tab', presses=4, interval=0.2)
        pausa_curta(0.3)
        pyautogui.write(str(opcao), interval=0.1)
        pausa_curta(0.4)
        
        pyautogui.press('tab', interval=0.2)
        pausa_curta(0.3)
        pyautogui.press('enter')
        pausa_curta(1.0)
        
        self.logger.registrar(f"Balancete parametrizado ({data_inicio} a {data_fim}, Opção: {opcao}).")

    def gerar_balancete(self, caminho_pasta: str, nome_arquivo: str, pos_x: int = 93, pos_y: int = 78) -> bool:
        """
        Exporta o relatório clicando na coordenada padrão, digitando o nome do arquivo,
        pressionando tab, abrindo a tela de pastas do Windows e salvando.
        """
        self.logger.registrar("Aguardando tela 'Pré-visualização' (tempo limite: 30s)...")
        janela_preview = esperar_tela("Pré-visualização", timeout=30, logger=self.logger)

        if not janela_preview:
            self.logger.registrar("❌ Tela 'Pré-visualização' não encontrada.")
            capturar_tela_erro("preview_balancete_nao_encontrado", self.logger)
            return False

        hwnd_preview, _ = janela_preview
        WindowManager.focar_e_restaurar(hwnd_preview)
        pausa_curta(0.6)

        # 1. Clica na coordenada padrão da tela de visualização
        pyautogui.click(x=pos_x, y=pos_y)
        self.logger.registrar(f"Clique na coordenada padrão ({pos_x}, {pos_y}) realizado.")
        pausa_curta(0.5)

        # 2. Digita o nome do arquivo (parâmetro passado) e dá Tab conforme solicitado
        pyautogui.write(nome_arquivo, interval=0.06)
        pausa_curta(0.3)
        pyautogui.press('tab')
        pausa_curta(0.4)
        
        # 3. Dá Enter para abrir a próxima tela (seleção/confirmação de diretório)
        pyautogui.press('enter')
        pausa_curta(1.0)

        # 4. Aguarda a janela "Salvar como" do Windows para navegar até a pasta de rede
        self.logger.registrar("Aguardando janela 'Salvar como' (tempo limite: 30s)...")
        janela_salvar = esperar_tela(("salvar", "salvar como"), timeout=30, logger=self.logger)

        if not janela_salvar:
            self.logger.registrar("❌ Tela 'Salvar como' não foi exibida.")
            capturar_tela_erro("janela_salvar_nao_exibida", self.logger)
            return False

        hwnd_salvar, _ = janela_salvar
        WindowManager.focar_e_restaurar(hwnd_salvar)
        pausa_curta(0.8)

        # 5. Navegação final para o caminho da rede via Alt+D e salvamento
        os.makedirs(caminho_pasta, exist_ok=True)
        pyautogui.hotkey('alt', 'd')
        pausa_curta(0.4)
        
        pyautogui.write(caminho_pasta, interval=0.05)
        pausa_curta(0.4)
        pyautogui.press('enter')
        pausa_curta(1.0)

        pyautogui.hotkey('alt', 'n')
        pausa_curta(0.4)
        
        pyautogui.hotkey('ctrl', 'a')
        pausa_curta(0.2)
        pyautogui.write(nome_arquivo, interval=0.06)
        pausa_curta(0.5)

        pyautogui.press('enter')
        pausa_curta(1.5)

        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        self.logger.registrar(f"Balancete gerado e salvo em '{caminho_completo}'.")
        return True