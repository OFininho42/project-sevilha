# Módulo RPA: Fortes AC (Setor Contábil)

Submódulo de automação em Python responsável por controlar a interface do sistema **Fortes AC**, realizando o logon, a troca automatizada de empresas e a extração de relatórios contábeis para o fluxo de migração.

---

## 📌 Escopo e Funcionalidades

- **Gerenciamento de Janelas e Telas**: Controle de janelas do Windows via API nativa (`pywin32`) para restaurar e dar foco às telas do Fortes AC.
- **Ambiente Isolado**: Alternância e preparação automatizada para a 3ª Área de Trabalho Virtual do Windows (`pyvda`).
- **Autenticação Automática**: Injeção de credenciais nos campos de texto da tela inicial e envio de confirmação (`F9`).
- **Seleção Flexível de Empresas**: Suporte para seleção por entrada manual via terminal, código único ou processamento em lote (listas/tuplas) via atalho `Ctrl + E`.
- **Extração de Balancetes**: Preenchimento automatizado de intervalo de datas, filtros, aguardo da pré-visualização e exportação por coordenadas de clique.
- **Rastreabilidade**: Envio do histórico de execução e capturas de erro para o arquivo `log_execucao.txt`.

---

## 🛠️ Requisitos e Bibliotecas

Certifique-se de que o ambiente Python possui as seguintes bibliotecas instaladas:

- `pywin32`: Interação direta com a API do Windows (busca de janelas via `HWND`).
- `pyvda`: Manipulação de áreas de trabalho virtuais do Windows.
- `pyautogui`: Envio de atalhos de teclado, digitação e cliques na tela.

Para instalar as dependências deste módulo:

```bash
pip install pywin32 pyvda pyautogui