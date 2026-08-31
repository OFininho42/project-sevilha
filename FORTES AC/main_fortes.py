from fortes_core import GerenciadorJanelas

def executar_main():
    # Caminho do executável ou atalho do programa
    caminho_fortes = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Fortes AC"
    
    # Nome parcial da janela que desejamos focar
    nome_janela = "Fortes AC"
    
    # Mensagem inicial informando que a automação começou
    print("Iniciando verificação da janela do Fortes AC...")
    
    # Instancia o gerenciador contido no arquivo fortes_core
    gerenciador = GerenciadorJanelas()
    
    # Executa a tentativa de focar ou abrir o programa
    # (Caso o programa precise ser aberto, lembre-se que aguardará 1 minuto)
    sucesso = gerenciador.executar_e_ativar_janela(caminho_fortes, nome_janela)
    
    # Exibe no terminal o resultado final do processo
    if sucesso:
        print("[SUCESSO] A janela do Fortes AC foi encontrada e ativada no primeiro plano!")
    else:
        print("[ERRO] Não foi possível encontrar ou abrir a janela do Fortes AC.")
        
    return sucesso

# Garante que o código só será executado se este arquivo for rodado diretamente
if __name__ == "__main__":
    executar_main()