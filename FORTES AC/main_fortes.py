import os
import pandas as pd
from fortes_core import Logger, FortesAutomator, garantir_fortes_aberto

def executar_automacao_lote():
    # ==========================================================================
    # 1. CONFIGURAÇÕES E PARÂMETROS INICIAIS
    # ==========================================================================
    caminho_planilha = r"C:\TEMPORÁRIOS\IMPORTANTE\Meu_Controle.xlsx"
    pasta_base_clientes = r"C:\TEMPORÁRIOS\CLIENTES"
    caminho_fortes = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Fortes AC"
    
    # Credenciais de acesso ao sistema
    usuario_fortes = "ROBOCONT"
    senha_fortes = "123"  # Substitua pela senha real do usuário ROBOCONT
    
    # Período fixo do balancete e opção do relatório
    data_inicio = "01012025"
    data_fim = "31122025"
    opcao_balancete = "1"
    
    logger = Logger()
    logger.registrar("==================================================")
    logger.registrar("=== INICIANDO EXECUÇÃO EM LOTE DO BALANCETE ===")
    logger.registrar("==================================================")

    # ==========================================================================
    # 2. LEITURA DA PLANILHA (10 PRIMEIRAS EMPRESAS)
    # ==========================================================================
    try:
        logger.registrar(f"Lendo planilha: {caminho_planilha}")
        
        # Lê apenas as 10 primeiras linhas sem cabeçalho (Coluna A = índice 0, Coluna B = índice 1)
        df = pd.read_excel(caminho_planilha, header=None, nrows=10)
        
        empresas_lista = []
        for _, linha in df.iterrows():
            codigo_raw = str(linha[0]).strip().split('.')[0]
            nome_raw = str(linha[1]).strip()
            
            if codigo_raw and nome_raw and codigo_raw.isdigit():
                empresas_lista.append((codigo_raw, nome_raw))
                
        logger.registrar(f"Total de empresas carregadas para teste: {len(empresas_lista)}")
        
    except Exception as e:
        logger.registrar("❌ Erro ao ler a planilha Excel. Verifique o caminho especificado.", e)
        return

    # ==========================================================================
    # 3. VERIFICAÇÃO DO SISTEMA E LOGON
    # ==========================================================================
    # Procura a janela do Fortes AC ativa ou abre via atalho caso não exista
    janela_fortes = garantir_fortes_aberto(caminho_fortes, timeout=120, logger=logger)
    if not janela_fortes:
        logger.registrar("❌ Execução interrompida: Janela do Fortes AC não encontrada ou não abriu.")
        return

    hwnd_janela, titulo = janela_fortes
    automator = FortesAutomator(logger)

    # Realiza o logon se a tela aberta for a janela inicial de login
    if "logon" in titulo.lower():
        sucesso_logon = automator.realizar_logon(hwnd_janela, usuario=usuario_fortes, senha=senha_fortes)
        if not sucesso_logon:
            logger.registrar("❌ Falha na autenticação. Encerrando automação.")
            return

    # ==========================================================================
    # 4. LOOPING DE PROCESSAMENTO E EXPORTAÇÃO
    # ==========================================================================
    for idx, (codigo, nome) in enumerate(empresas_lista, start=1):
        logger.registrar(f"\n--- [{idx}/{len(empresas_lista)}] Empresa: {codigo} - {nome} ---")
        
        try:
            # Seleciona a empresa via Ctrl+E
            if not automator.escolher_empresa(codigo):
                logger.registrar(f"⚠️ Troca para a empresa {codigo} falhou. Indo para a próxima.")
                continue

            # Preenche o período e abre a pré-visualização
            automator.preencher_balancete(
                data_inicio=data_inicio,
                data_fim=data_fim,
                opcao=opcao_balancete
            )

            # Estruturação da pasta e do arquivo no formato: Código - Nome
            pasta_empresa = os.path.join(pasta_base_clientes, f"{codigo} - {nome}")
            nome_arquivo_pdf = f"{codigo} - {nome} - Balancete 31.12.2025.pdf"

            # Salva o arquivo no diretório criado
            sucesso_exportacao = automator.gerar_balancete(
                caminho_pasta=pasta_empresa,
                nome_arquivo=nome_arquivo_pdf,
                pos_x=93,
                pos_y=78,
                letra_atalho='d',
                pos_btn_x=1172,
                pos_btn_y=454
            )

            if sucesso_exportacao:
                logger.registrar(f"✅ Balancete da empresa {codigo} exportado com sucesso!")
            else:
                logger.registrar(f"❌ Não foi possível salvar o balancete da empresa {codigo}.")

        except Exception as e:
            logger.registrar(f"❌ Erro durante o processamento da empresa {codigo}", e)

    logger.registrar("\n==================================================")
    logger.registrar("=== EXECUÇÃO FINALIZADA ===")
    logger.registrar("==================================================")

if __name__ == "__main__":
    executar_automacao_lote()