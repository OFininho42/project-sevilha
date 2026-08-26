import datetime
import os
import time
import traceback
import win32api
import win32con
import win32gui
from pyvda import VirtualDesktop, get_virtual_desktops

# Lista global de erros
lista_erros = []


# ==============================================================================
# CLASSE DE USUÁRIO - SUBSTITUA SUAS CREDENCIAIS ABAIXO
# ==============================================================================
class Usuario:

    def __init__(self):
        # ⚠️ SUBSITUA OS VALORES DAS DUAS LINHAS ABAIXO COM SEUS DADOS:
        self.usuario = "ROBOCONT"
        self.senha = "123"

        # Configurações fixas exigidas
        self.sub_sistema = "Setor Contábil"
        self.empresa = []


def registrar_erro(contexto, erro):
    mensagem_erro = (
        f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro em"
        f" '{contexto}': {str(erro)}\n{traceback.format_exc()}"
    )
    lista_erros.append(mensagem_erro)
    print(f"⚠️ {mensagem_erro}")


def gerenciar_terceira_area():
    try:
        total_desktops = len(get_virtual_desktops())
        if total_desktops >= 3:
            print(
                f"Encontradas {total_desktops} área(s). Removendo a 3ª e"
                " superiores..."
            )
            while len(get_virtual_desktops()) >= 3:
                ultimo_indice = len(get_virtual_desktops())
                VirtualDesktop(ultimo_indice).remove()
                time.sleep(0.2)

        print("Garantindo a criação de uma 3ª área limpa...")
        while len(get_virtual_desktops()) < 3:
            VirtualDesktop.create()
            time.sleep(0.2)

        VirtualDesktop(3).go()
        print("3ª área de trabalho pronta e focada!")
    except Exception as e:
        registrar_erro("Gerenciamento de Áreas de Trabalho", e)


def buscar_janela_logon():
    janela_encontrada = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            titulo = win32gui.GetWindowText(hwnd)
            if titulo and "logon" in titulo.lower():
                janela_encontrada.append((hwnd, titulo))
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        registrar_erro("Busca de Janela Logon", e)

    return janela_encontrada[0] if janela_encontrada else None


def mapear_telas_ativas():
    telas = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            titulo = win32gui.GetWindowText(hwnd)
            classe = win32gui.GetClassName(hwnd)
            if titulo:
                telas.append(
                    f"HWND: {hwnd} | Classe: {classe} | Título: {titulo}"
                )
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        registrar_erro("Mapeamento de Telas Ativas", e)

    return telas


def mapear_objetos_janela(hwnd_pai):
    objetos = []

    def callback(hwnd, extra):
        titulo = win32gui.GetWindowText(hwnd)
        classe = win32gui.GetClassName(hwnd)
        objetos.append(
            f"HWND: {hwnd} | Classe: {classe} | Texto/Título: {titulo}"
        )
        return True

    try:
        win32gui.EnumChildWindows(hwnd_pai, callback, None)
    except Exception as e:
        registrar_erro("Mapeamento de Objetos do Logon", e)

    return objetos


def preencher_e_confirmar_logon(hwnd_logon, credenciais: Usuario):
    """Identifica os campos de texto por posição Y, preenche usuário/senha e envia F9."""
    try:
        edits = []

        # 1. Coleta todas as caixas de texto (TDLEdit) e suas coordenadas na tela
        def callback_edits(hwnd, extra):
            if win32gui.GetClassName(hwnd) == "TDLEdit":
                rect = win32gui.GetWindowRect(hwnd)
                top_y = rect[1]  # Coordenada Y (topo do controle)
                edits.append((hwnd, top_y))
            return True

        win32gui.EnumChildWindows(hwnd_logon, callback_edits, None)

        # 2. Ordena do topo para o fundo da janela (menor Y para maior Y)
        edits.sort(key=lambda item: item[1])

        if len(edits) < 2:
            raise Exception(
                f"Número insuficiente de campos de texto localizados ({len(edits)} encontrados)."
            )

        hwnd_usuario = edits[0][0]  # Primeiro campo superior (Usuário)
        hwnd_senha = edits[1][0]  # Segundo campo (Senha)

        print(
            f"Preenchendo Usuário (HWND: {hwnd_usuario}) e Senha (HWND:"
            f" {hwnd_senha})..."
        )

        # 3. Preenche os campos de texto
        win32gui.SendMessage(
            hwnd_usuario, win32con.WM_SETTEXT, 0, str(credenciais.usuario)
        )
        win32gui.SendMessage(
            hwnd_senha, win32con.WM_SETTEXT, 0, str(credenciais.senha)
        )

        time.sleep(0.5)

        # 4. Traz a janela de Logon para o primeiro plano
        win32gui.SetForegroundWindow(hwnd_logon)
        time.sleep(0.3)

        # 5. Envia o comando da tecla F9
        print("Enviando tecla 'F9' para confirmar o logon...")
        win32api.keybd_event(win32con.VK_F9, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_F9, 0, win32con.KEYEVENTF_KEYUP, 0)

    except Exception as e:
        registrar_erro("Preenchimento e Envio de Logon (F9)", e)


def salvar_relatorio(caminho_dir, conteudo):
    try:
        os.makedirs(caminho_dir, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_dir, "relatorio_execucao.txt")

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)

        print(f"Relatório salvo em: {caminho_arquivo}")
    except Exception as e:
        registrar_erro("Gravação do Arquivo TXT", e)


def main():
    pasta_destino = r"C:\TEMPORÁRIOS\OUTROS"
    credenciais = Usuario()

    # 1. Limpeza e foco na 3ª Área
    gerenciar_terceira_area()
    time.sleep(1)

    # 2. Execução do Fortes AC
    caminho_programa = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Fortes AC"
    print(f"Iniciando programa: {caminho_programa}")

    try:
        os.startfile(caminho_programa)
    except Exception as e:
        registrar_erro("Iniciar Fortes AC (os.startfile)", e)

    # 3. Looping de Espera de até 2 Minutos (120 segundos)
    print("Aguardando a abertura da tela 'Logon' (Tempo limite: 2 minutos)...")
    tempo_inicio = time.time()
    tempo_limite_segundos = 120
    janela_logon = None

    while (time.time() - tempo_inicio) < tempo_limite_segundos:
        janela_logon = buscar_janela_logon()
        if janela_logon:
            break
        time.sleep(1)

    # 4. Processamento dos Resultados

    if not janela_logon:
        print("❌ Tempo limite excedido. A tela 'Logon' não foi encontrada.")

        relatorio = [
            "==================================================",
            "       RELATÓRIO DE FALHA DE INICIALIZAÇÃO       ",
            "==================================================",
            (
                "Data/Hora:"
                f" {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            (
                "Status: O Fortes AC não inicializou dentro do tempo limite de 2"
                " minutos."
            ),
            "\n==================================================",
            "               REGISTRO DE ERROS                  ",
            "==================================================",
        ]

        if lista_erros:
            relatorio.extend(lista_erros)
        else:
            relatorio.append("Nenhum erro de execução capturado no código.")

        salvar_relatorio(pasta_destino, "\n".join(relatorio))

    else:
        hwnd_logon, titulo_logon = janela_logon
        print(f"✅ Tela 'Logon' detectada! (HWND: {hwnd_logon})")

        # Mapeia telas e controles antes/durante o preenchimento
        telas_ativas = mapear_telas_ativas()
        objetos_logon = mapear_objetos_janela(hwnd_logon)

        # Executa o preenchimento dos campos e pressiona F9
        preencher_e_confirmar_logon(hwnd_logon, credenciais)

        relatorio = [
            "==================================================",
            "     RELATÓRIO DE SUCESSO E MAPEAMENTO - LOGON    ",
            "==================================================",
            (
                "Data/Hora:"
                f" {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            f"Janela Alvo: {titulo_logon} (HWND: {hwnd_logon})\n",
            "==================================================",
            "LISTA 1: TODAS AS TELAS ATIVAS NO SISTEMA",
            "==================================================",
        ]
        relatorio.extend([f"- {tela}" for tela in telas_ativas])

        relatorio.append("\n==================================================")
        relatorio.append("LISTA 2: OBJETOS / CONTROLES DA TELA DE LOGON")
        relatorio.append("==================================================")
        relatorio.extend([f"- {obj}" for obj in objetos_logon])

        relatorio.append("\n==================================================")
        relatorio.append("REGISTRO DE ERROS DURANTE A EXECUÇÃO")
        relatorio.append("==================================================")

        if lista_erros:
            relatorio.extend(lista_erros)
        else:
            relatorio.append("Nenhum erro de código ocorreu durante o processo.")

        salvar_relatorio(pasta_destino, "\n".join(relatorio))


if __name__ == "__main__":
    main()