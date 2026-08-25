from pathlib import Path
import re
import unicodedata
import openpyxl as opxl


def limpar_nome_pasta(nome):
    """Remove apenas caracteres proibidos no Windows para nomear a pasta."""
    return re.sub(r'[\\/*?:"<>|]', '', str(nome)).strip()


def normalizar_para_comparacao(texto):
    """Remove acentos, símbolos e espaços para comparar equivalência de nomes."""
    # Remove acentos (ex: "Á" vira "A")
    texto_sem_acento = (
        unicodedata.normalize('NFKD', str(texto))
        .encode('ASCII', 'ignore')
        .decode('utf-8')
    )
    # Mantém apenas letras e números, em minúsculas
    return re.sub(r'[^a-zA-Z0-9]', '', texto_sem_acento).lower()


class Controle:
    wb_path = r'C:\TEMPORÁRIOS\IMPORTANTE\Meu_Controle.xlsx'
    wb = opxl.load_workbook(wb_path)
    ws = wb['Planilha1']

    codempresa = 'A'
    nomeempresa = 'B'


meu_controle = Controle()

# 1. Mapeia as pastas já existentes no disco usando a chave normalizada
caminho_clientes = Path(r'C:\TEMPORÁRIOS\CLIENTES')
caminho_clientes.mkdir(parents=True, exist_ok=True)

# Dicionário: { '101empresasa': '101 - EMPRESA SA' }
pastas_existentes_norm = {
    normalizar_para_comparacao(p.name): p.name
    for p in caminho_clientes.iterdir()
    if p.is_dir()
}

# 2. Varre o Excel e cria apenas se a chave normalizada não existir
print('=== PROCESSANDO PASTAS ===')
novas_criadas = 0

for linha in range(2, meu_controle.ws.max_row + 1):
    val_a = meu_controle.ws[f'{meu_controle.codempresa}{linha}'].value
    val_b = meu_controle.ws[f'{meu_controle.nomeempresa}{linha}'].value

    if val_a is not None or val_b is not None:
        val_a_str = str(val_a).strip() if val_a is not None else ''
        val_b_str = str(val_b).strip() if val_b is not None else ''

        nome_bruto = f'{val_a_str} - {val_b_str}'
        nome_limpo = limpar_nome_pasta(nome_bruto)
        chave_excel = normalizar_para_comparacao(nome_bruto)

        if chave_excel and chave_excel not in pastas_existentes_norm:
            caminho_nova_pasta = caminho_clientes / nome_limpo
            caminho_nova_pasta.mkdir(parents=True, exist_ok=True)

            # Adiciona ao mapa para evitar duplicatas dentro do próprio Excel
            pastas_existentes_norm[chave_excel] = nome_limpo

            print(f'[CRIADA] {nome_limpo}')
            novas_criadas += 1
        else:
            pasta_atual = pastas_existentes_norm.get(chave_excel, 'Já existente')
            print(f'[IGNORADA - JÁ EXISTE] {nome_limpo} -> (Pasta no disco: "{pasta_atual}")')

print(f'\nProcesso concluído! {novas_criadas} nova(s) pasta(s) criada(s).')