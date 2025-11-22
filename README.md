# Controle de Gastos
Projeto em Python, utilizando Streamlit e SQLite para gestão de gastos mensais.

# Observações gerais
- Criar os Modelos das Tabelas
  - tbTipoPagamento
  - tbMesAnoPagamento
  - tbPagamento
  - tbValorPagamento
    - Incluir no **`__init__.py`** da pasta Models

- Criar Controllers das Tabelas
  - Incluir no **`__init__.py`** da pasta Controller
  - Testar chamada das funções


| Tabela            | Model | Controller |
| ---------         | :---: | :---:      |
| tbTipoPagamento   |  ✅   |  ✅       |
| tbMesAnoPagamento |  ✅   |  ✅       |
| tbPagamento       |  ✅   |  ✅       |
| tbValorPagamento  |  🔄   |🔄         |
