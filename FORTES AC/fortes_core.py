import time
import pyautogui
import pygetwindow as gw
import psutil
from pywinauto import Desktop

def obter_pids_do_executavel(nome_executavel: str) -> list:
    """
    Busca e retorna uma lista com os PIDs (Process IDs)
    de todas as instâncias do programa informadas em execução.
    """
    pids = []
    for processo in psutil.process_iter(['pid', 'name']):
        try:
            if processo.info['name'] and processo.info['name'].lower() == nome_executavel.lower():
                pids.append(processo.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return pids


def fechar_subjanelas_ac():
    """
    Localiza todas as janelas do AC.exe que NÃO começam com 'Fortes AC'
    e pressiona a tecla 'ESC' em cada uma delas até que todas sejam fechadas.
    """
    EXECUTAVEL_ALVO = "AC.exe"
    PREFIXO_PRINCIPAL = "Fortes AC"
    MAX_TENTATIVAS = 20  # Trava de segurança contra loops infinitos

    print(f"--- INICIANDO LIMPEZA DE JANELAS DO {EXECUTAVEL_ALVO} ---")

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        # 1. Obtém os PIDs atualizados do programa
        pids = obter_pids_do_executavel(EXECUTAVEL_ALVO)

        if not pids:
            print(f"O programa '{EXECUTAVEL_ALVO}' não está rodando no momento.")
            return

        desktop = Desktop(backend="win32")
        janelas_para_fechar = []

        # 2. Varre as janelas visíveis vinculadas aos PIDs do programa
        for pid in pids:
            janelas = desktop.windows(process=pid)
            for janela in janelas:
                titulo = janela.window_text().strip()

                # Verifica se a janela está visível e NÃO começa com 'Fortes AC'
                if titulo and janela.is_visible():
                    if not titulo.startswith(PREFIXO_PRINCIPAL):
                        janelas_para_fechar.append((janela, titulo))

        # 3. Condição de parada: Se não houver sub-janelas, encerra a limpeza
        if not janelas_para_fechar:
            print("\n✅ Sucesso! Nenhuma sub-janela pendente. Resta apenas a tela principal.")
            break

        print(f"\n[Ciclo {tentativa}/{MAX_TENTATIVAS}] Encontrada(s) {len(janelas_para_fechar)} sub-janela(s):")

        # 4. Looping para focar e pressionar ESC em cada janela secundária
        for janela, titulo in janelas_para_fechar:
            try:
                print(f" -> Fechando tela: \"{titulo}\"")

                # Foca a janela para garantir que receba a tecla
                janela.set_focus()
                time.sleep(0.2)  # Pausa rápida para o Windows alternar o foco

                # Envia o comando da tecla ESC
                janela.type_keys("{ESC}")
                time.sleep(0.5)  # Tempo para a janela fechar e sumir da tela

            except Exception as erro:
                print(f"    ⚠️ Erro ao tentar fechar \"{titulo}\": {erro}")

    else:
        print("\n⚠️ Limite de tentativas atingido. Verifique se existe alguma tela solicitando confirmação manual.")


if __name__ == "__main__":
    fechar_subjanelas_ac()


def preencher_campo_e_confirmar(valor_inteiro: int = 100, x: int = 682, y: int = 13, titulo_janela: str = "Fortes AC"):
    """
    Verifica se a janela informada existe e está aberta. 
    Se existir, ativa a janela e preenche o campo. 
    Caso contrário, exibe uma mensagem informando que a janela não existe e cancela a ação.

    Parâmetros:
        valor_inteiro (int): O número inteiro a ser digitado (padrão: 100).
        x (int): Posição horizontal do clique na tela (padrão: 682).
        y (int): Posição vertical do clique na tela (padrão: 13).
        titulo_janela (str): Título (ou parte do título) da janela a ser focada (padrão: "Fortes AC").
    """
    # 1. Procura por todas as janelas abertas que contenham o título desejado
    janelas = gw.getWindowsWithTitle(titulo_janela)

    # 2. Verifica se a lista de janelas está vazia (janela não encontrada)
    if not janelas:
        print(f"❌ A janela '{titulo_janela}' não foi encontrada ou não está aberta. Ação cancelada.")
        return

    # 3. Pega a primeira janela correspondente encontrada
    janela = janelas[0]

    print(f"🔍 Janela '{titulo_janela}' localizada. Ativando...")

    try:
        # Se a janela estiver minimizada, restaura ela para o tamanho normal
        if janela.isMinimized:
            janela.restore()
        
        # Traz a janela para o primeiro plano da tela
        janela.activate()
        time.sleep(1) # Pausa rápida de 1 segundo para garantir que a janela apareceu na frente
    except Exception as erro:
        print(f"⚠️ Erro ao tentar ativar a janela: {erro}")
        return

    # Configuração de pausa padrão do PyAutoGUI
    pyautogui.PAUSE = 0.3

    print("Iniciando digitação em 3 segundos...")
    time.sleep(3)

    # 4. Clica na posição especificada
    print(f"1. Clicando nas coordenadas X={x}, Y={y}")
    pyautogui.click(x=x, y=y)

    # 5. Digita o valor recebido no parâmetro
    print(f"2. Digitando o valor: {valor_inteiro}")
    pyautogui.write(str(valor_inteiro), interval=0.05)

    # 6. Pressiona a tecla Tab
    print("3. Pressionando a tecla Tab")
    pyautogui.press('tab')

    # 7. Pressiona a tecla Enter
    print("4. Pressionando a tecla Enter")
    pyautogui.press('enter')

    print("✅ Execução concluída com sucesso!")


if __name__ == "__main__":
    # Teste de execução chamando a função com o valor desejado
    preencher_campo_e_confirmar(valor_inteiro=8699)

def gerar_balancete(data_inicio: str = "01012025", data_fim: str = "31122025", opcao: str = "1", x: int = 284, y: int = 63):
    """
    Realiza a sequência automatizada de comandos de clique e teclado
    para preenchimento e geração do balancete na tela do sistema.

    Parâmetros:
        data_inicio (str): Data inicial no formato DDMMAAAA (padrão: "01012025").
        data_fim (str): Data final no formato DDMMAAAA (padrão: "31122025").
        x (int): Coordenada horizontal do primeiro clique (padrão: 284).
        y (int): Coordenada vertical do primeiro clique (padrão: 63).
    """
    # Define um intervalo global de segurança (em segundos) entre cada comando do PyAutoGUI.
    # Isso impede que o Python envie comandos mais rápido do que a tela consegue responder.
    pyautogui.PAUSE = 0.3

    print("Iniciando a automação do Balancete...")
    print("Aguardando 3 segundos para garantir foco na tela...")
    time.sleep(3)

    # 1. Clica nas coordenadas especificadas (x=284, y=63)
    print(f"1. Clicando no ponto X={x}, Y={y}")
    pyautogui.click(x=x, y=y)

    # 2. Pressiona a tecla Tab duas vezes
    print("2. Pressionando Tab (2x)...")
    pyautogui.press('tab', presses=2, interval=0.1)

    # 3. Digita a data inicial (01/01/2025)
    print(f"3. Digitando a data inicial: {data_inicio}")
    pyautogui.write(data_inicio, interval=0.05)

    # 4. Pressiona a tecla Tab uma vez
    print("4. Pressionando Tab (1x)...")
    pyautogui.press('tab')

    # 5. Digita a data final (31/12/2025)
    print(f"5. Digitando a data final: {data_fim}")
    pyautogui.write(data_fim, interval=0.05)

    # 6. Pressiona a tecla Tab 4 vezes
    print("6. Pressionando Tab (4x)...")
    pyautogui.press('tab', presses=4, interval=0.1)

    # 7. Digita a opcao "1"
    print(f"7. Digitando a opcao: {opcao}")
    pyautogui.write(opcao, interval=0.05)

    # 8. Pressiona a tecla Tab 4 vezes
    print("6. Pressionando Tab (4x)...")
    pyautogui.press('tab', presses=1, interval=0.1)

    # 9. Pressiona Enter para confirmar a geração
    print("7. Pressionando Enter para gerar...")
    pyautogui.press('enter')

    print("✅ Função gerar_balancete() executada com sucesso!")


if __name__ == "__main__":
    # Execução de teste da função
    gerar_balancete()