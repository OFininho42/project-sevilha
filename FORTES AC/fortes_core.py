import time
import subprocess
import pygetwindow as gw

class GerenciadorJanelas:
    
    def ativar_janela_por_nome(self, nome_parcial):
        try:
            # Busca todas as janelas que contenham o nome informado
            janelas = gw.getWindowsWithTitle(nome_parcial)
            
            if janelas:
                janela = janelas[0]
                
                # Restaura a janela se estiver minimizada
                if janela.isMinimized:
                    janela.restore()
                    
                # Foca a janela no primeiro plano
                janela.activate()
                return True
                
            return False
        except Exception:
            return False

    def executar_e_ativar_janela(self, caminho_exe, nome_parcial):
        # Tenta ativar a janela caso já esteja aberta
        if self.ativar_janela_por_nome(nome_parcial):
            return True
        
        try:
            # Executa o arquivo .exe em segundo plano
            subprocess.Popen(caminho_exe)
            
            # Aguarda 60 segundos para o programa carregar completamente
            time.sleep(60)
            
            # Tenta ativar a janela novamente após a inicialização
            return self.ativar_janela_por_nome(nome_parcial)
        except Exception:
            return False
