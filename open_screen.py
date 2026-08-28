import time
import re
from pywinauto import Desktop

# --- PARÂMETROS ---
nome_janela = 'Fortes AC 8.27.0.1 - Setor Contábil'  # Mantenha o nome ajustado por você


def verificar_e_ajustar_janela(titulo, espera=0.8):
    """
    Verifica se a tela existe. Se existir, força a restauração e o foco.
    Retorna True se a tela foi encontrada e ativada, ou False caso contrário.
    """
    padrao_regex = f".*{re.escape(titulo)}.*"
    janela = None

    for backend in ["uia", "win32"]:
        desktop = Desktop(backend=backend)
        try:
            j = desktop.window(title_re=padrao_regex)
            if j.exists(timeout=1.5):
                janela = j
                break
        except Exception:
            continue

    if not janela:
        print(f"[RESULTADO] A tela '{titulo}' NÃO foi encontrada.")
        return False

    print(f"[RESULTADO] A tela '{titulo}' FOI encontrada com sucesso!")

    try:
        if janela.is_minimized():
            print("Estado: Minimizada. Restaurando janela...")
            janela.restore()
        else:
            print("Estado: Aberta. Minimizando e restaurando...")
            janela.minimize()
            time.sleep(espera)
            janela.restore()

        time.sleep(espera)
        janela.set_focus()
        time.sleep(0.5)  # Pausa para estabilização do Windows
        print("Janela ativada e pronta para uso.")
        return True

    except Exception as e:
        print(f"Aviso ao alterar o estado da janela: {e}")
        return True


# Garante que NADA roda automaticamente ao importar este arquivo
if __name__ == "__main__":
    verificar_e_ajustar_janela(nome_janela)