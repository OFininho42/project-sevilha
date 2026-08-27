import os
import time
import pyautogui
import pygetwindow as gw

def funcao_previa():
    # Cole aqui o código ou lógica da sua função anterior
    print("Executando etapa prévia...")


def executar_automacao_fortes():
    # 0. Executa a função prévia obrigatoriamente antes do resto do fluxo
    funcao_previa()

    titulo_fortes = 'Fortes AC 8.27.0.1 - Setor Contábil'
    titulo_balancete = 'Balancete Contábil'
    diretorio_log = r'C:\TEMPORÁRIOS\OUTROS'
    arquivo_log = os.path.join(diretorio_log, 'log_execucao.txt')

    # 1. Verifica se a janela do Fortes existe
    janelas_fortes = gw.getWindowsWithTitle(titulo_fortes)
    
    if not janelas_fortes:
        os.makedirs(diretorio_log, exist_ok=True)
        with open(arquivo_log, 'a', encoding='utf-8') as f:
            data_hora = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{data_hora}] A tela '{titulo_fortes}' não foi encontrada.\n")
        return

    # Foca na janela do Fortes
    janela_fortes = janelas_fortes[0]
    janela_fortes.activate()
    time.sleep(1)

    # Clique nas coordenadas (X=360, Y=87) relativas à janela
    pos_x = janela_fortes.left + 360
    pos_y = janela_fortes.top + 87
    pyautogui.click(pos_x, pos_y)

    # 2. Aguarda a tela 'Balancete Contábil' por até 2 minutos (120s)
    tempo_inicio = time.time()
    timeout = 120
    janela_balancete_localizada = False

    while time.time() - tempo_inicio < timeout:
        janelas_balancete = gw.getWindowsWithTitle(titulo_balancete)
        if janelas_balancete:
            janela_balancete = janelas_balancete[0]
            janela_balancete.activate()
            janela_balancete_localizada = True
            break
        time.sleep(1)

    if not janela_balancete_localizada:
        return

    time.sleep(0.5)

    # 3. Comandos de teclado na tela do Balancete
    pyautogui.press('tab', presses=2, interval=0.1)
    pyautogui.write('01012025', interval=0.05)
    pyautogui.press('tab', interval=0.1)
    pyautogui.write('31122025', interval=0.05)
    pyautogui.press('tab', presses=4, interval=0.1)
    pyautogui.write('1', interval=0.05)
    pyautogui.press('tab', interval=0.1)
    pyautogui.press('enter')

if __name__ == '__main__':
    executar_automacao_fortes()