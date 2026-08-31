from fortes_core import FortesACAutomation

# Instancia a automação
bot = FortesACAutomation()

# Execução ordenada do fluxo
if bot.verificar_janela_aberta():
    bot.fechar_janelas_adjacentes()

# Inicia a aplicação e realiza logon com a empresa 8 (ou informe outra empresa no argumento)
bot.iniciar_e_realizar_logon(codigo_empresa=8)