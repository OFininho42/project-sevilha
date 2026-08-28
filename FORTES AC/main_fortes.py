import os
import sys
import time
import pyautogui
import pandas as pd

# Importamos as classes e funções do nosso arquivo core
from fortes_core import Logger, FortesAutomator, garantir_fortes_aberto, capturar_tela_erro

# ==============================================================================
# CONFIGURAÇÕES DE CAMINHOS E PARÂMETROS DA PLANILHA
# ==============================================================================

# Caminho do executável do sistema Fortes no seu ambiente
CAMINHO_FORTES_EXE = r"C:\Fortes\AC\FortesAC.exe" 

# Caminho da pasta de rede onde os relatórios gerados serão salvos
PASTA_DESTINO_RELATORIO = r"\\192.168.0.2\Fortes\AC"

# Caminho da sua planilha de controle
CAMINHO_PLANILHA = r"C:\TEMPORÁRIOS\IMPORTANTE\Meu_Controle.xlsx"

# Parâmetros fixos do Balancete
DATA_INICIO_FILTRO = "01012025"
DATA_FIM_FILTRO = "31122025"
OPCAO_FILTRO = "1"


# ==============================================================================
# FUNÇÃO PARA LER OS PARÂMETROS DA PLANILHA (LIMITADO AOS 10 PRIMEIROS)
# ==============================================================================

def carregar_primeiras_empresas_da_planilha(caminho_arquivo: str, limite: int = 10) -> list:
    """
    Lê a planilha Excel de controle, pega apenas as 10 primeiras empresas 
    e retorna uma lista limpa com os códigos.
    """
    try:
        if not os.path.exists(caminho_arquivo):
            print(f"❌ Planilha não encontrada no caminho: {caminho_arquivo}")
            return []

        df = pd.read_excel(caminho_arquivo, sheet_name=0)
        nome_coluna = 'Empresa' 
        
        if nome_coluna not in df.columns:
            nome_coluna = df.columns[0]
            
        # Pega todos os valores válidos, converte para string e fatia para pegar apenas os 10 primeiros
        empresas = df[nome_coluna].dropna().astype(str).str.strip().tolist()
        empresas_limitadas = empresas[:limite]
        
        return empresas_limitadas

    except Exception as e:
        print(f"❌ Erro ao ler a planilha de controle: {e}")
        return []


# ==============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# ==============================================================================

def executar_automacao():
    # 1. Inicializa o serviço de log para registrar todas as etapas no arquivo TXT
    logger = Logger()
    logger.registrar("=== Iniciando execução da automação do Fortes AC (Lote de 10) ===")

    try:
        # 2. Carrega estritamente as 10 primeiras empresas da planilha de controle
        logger.registrar(f"Lendo parâmetros da planilha: {CAMINHO_PLANILHA}")
        lista_empresas = carregar_primeiras_empresas_da_planilha(CAMINHO_PLANILHA, limite=10)

        if not lista_empresas:
            logger.registrar("❌ Nenhuma empresa encontrada na planilha ou falha na leitura. Abortando.")
            return

        logger.registrar(f"Empresas carregadas para processamento (máx. 10): {lista_empresas}")

        # 3. Instancia o automador com a cadência humana configurada
        automator = FortesAutomator(logger=logger)

        # 4. Executa a verificação prévia e o processamento de cada empresa
        for empresa in lista_empresas:
            logger.registrar(f"\n--- Analisando a Empresa: {empresa} ---")

            # Nome esperado do arquivo na pasta de destino
            nome_arquivo = f"Balancete_Empresa_{empresa}.rpf"
            caminho_arquivo_salvo = os.path.join(PASTA_DESTINO_RELATORIO, nome_arquivo)

            # 🔍 ETAPA PRÉVIA: Verifica se o arquivo já existe antes de abrir o Fortes
            if os.path.exists(caminho_arquivo_salvo):
                logger.registrar(f"⏩ Arquivo já existe para a Empresa {empresa} ('{nome_arquivo}'). Pulando para a próxima...")
                continue  # Pula todo o resto do loop e vai direto para a próxima empresa

            # Se o arquivo não existir, aí sim garante que o Fortes está aberto para processar
            janela_fortes = garantir_fortes_aberto(
                caminho_fortes=CAMINHO_FORTES_EXE, 
                timeout=30, 
                logger=logger
            )

            if not janela_fortes:
                logger.registrar("❌ Não foi possível acessar a janela do Fortes AC. Abortando processo.")
                return

            # Seleciona a empresa atual
            sucesso_empresa = automator.escolher_empresa(empresas=empresa)
            if not sucesso_empresa:
                logger.registrar(f"❌ Falha ao selecionar a empresa {empresa}. Pulando para a próxima...")
                # Garante o envio de ESC duplo para limpar resíduos da tela de empresa
                pyautogui.press('esc')
                time.sleep(0.5)
                pyautogui.press('esc')
                time.sleep(0.8)
                continue

            # Preenche os parâmetros do Balancete
            automator.preencher_balancete(
                data_inicio=DATA_INICIO_FILTRO,
                data_fim=DATA_FIM_FILTRO,
                opcao=OPCAO_FILTRO
            )

            # Exporta e salva o relatório na pasta de rede
            sucesso_geracao = automator.gerar_balancete(
                caminho_pasta=PASTA_DESTINO_RELATORIO,
                nome_arquivo=nome_arquivo
            )

            if sucesso_geracao:
                logger.registrar(f"✅ Balancete da Empresa {empresa} gerado com sucesso!")
                
                # Pressiona ESC duas vezes para limpar as telas antes do próximo loop
                logger.registrar("Pressionando ESC duas vezes para retornar ao menu principal...")
                pyautogui.press('esc')
                time.sleep(0.5)
                pyautogui.press('esc')
                time.sleep(0.8)
            else:
                logger.registrar(f"❌ Erro ao gerar o balancete da Empresa {empresa}.")
                
                # Em caso de erro, envia ESC para tentar destravar a interface
                pyautogui.press('esc')
                time.sleep(0.5)
                pyautogui.press('esc')
                time.sleep(0.8)

        logger.registrar("=== Processamento do lote de empresas finalizado! ===")

    except Exception as e:
        logger.registrar(f"❌ Erro crítico não esperado durante a execução: {str(e)}", erro=e)
        capturar_tela_erro("erro_critico_main", logger)


# ==============================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    executar_automacao()