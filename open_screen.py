import time
import re
from pywinauto import Desktop

# --- PARÂMETRO ---
nome_janela = 'abcd'  # Insira o nome ou parte da tela


def verificar_e_ajustar_janela(titulo, espera=0.5):
    """
    Verifica se a tela existe e imprime o resultado no console.
    Se existir, ajusta o estado (minimizar/restaurar).
    """
    padrao_regex = f".*{re.escape(titulo)}.*"
    janela = None

    # Tenta encontrar a janela nos dois backends do Windows
    for backend in ["uia", "win32"]:
        desktop = Desktop(backend=backend)
        try:
            j = desktop.window(title_re=padrao_regex)
            if j.exists(timeout=1):
                janela = j
                break
        except Exception:
            continue

    # Se a janela não for encontrada
    if not janela:
        print(f"[RESULTADO] A tela '{titulo}' NÃO foi encontrada.")
        return False

    # Se a janela for encontrada
    print(f"[RESULTADO] A tela '{titulo}' FOI encontrada com sucesso!")

    # Alterna e valida o estado da janela
    try:
        if janela.is_minimized():
            print("Estado atual: Minimizada. Restaurando janela...")
            janela.restore()
        else:
            print("Estado atual: Aberta. Minimizando e restaurando janela...")
            janela.minimize()
            time.sleep(espera)
            janela.restore()
        
        time.sleep(espera)
        janela.set_focus()
        print("Janela ativada e pronta para uso.")

    except Exception as e:
        print(f"Aviso ao alterar o estado da janela: {e}")

    return True


# --- EXECUÇÃO ---
verificar_e_ajustar_janela(nome_janela)