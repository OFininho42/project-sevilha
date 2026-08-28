from pynput import mouse

def obter_ultimo_clique():
    posicao = None

    def ao_clicar(x, y, botao, pressionado):
        nonlocal posicao
        if pressionado:
            posicao = (x, y)
            return False  # Para a escuta no primeiro clique capturado

    with mouse.Listener(on_click=ao_clicar) as listener:
        listener.join()

    return posicao

# Exemplo de uso:
ponto = obter_ultimo_clique()
print(f"Última posição capturada: {ponto}")  # Retorna uma tupla: (x, y)