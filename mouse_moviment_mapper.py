from pynput import mouse

def ao_clicar(x, y, botao, pressionado):
    # Executa apenas quando o botão do mouse é pressionado (down)
    if pressionado:
        print(f"Coordenada capturada: X={x}, Y={y} (Botão: {botao.name})")
        
        # Interrompe o listener imediatamente após o primeiro clique (break)
        return False

print("Aguardando clique do mouse na tela...")

# Inicia o monitoramento em tempo real
with mouse.Listener(on_click=ao_clicar) as escutador:
    escutador.join()

print("Captura finalizada.")