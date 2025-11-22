from Models import gerarLog
from Controller import funcoesUsuario, funcoesTipoPagamento, funcoesMesAnoPagamento, funcoesPagamento
from PaginasStreamlit.middleware_auth import obter_codigo_usuario

import streamlit as st

# Verificar se o usuário está logado antes de carregar filtros
if 'usuario_logado' in st.session_state and st.session_state.usuario_logado:
    codigo_usuario = obter_codigo_usuario()
    
    # Carregar anos e meses disponíveis do usuário logado
    mesesFiltro = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    anosFiltro = funcoesMesAnoPagamento.get("consultarAnosDisponiveis")(codigo_usuario)

    st.session_state.anosSelecionados = st.sidebar.multiselect(label="Filtrar Anos", options=anosFiltro, default=[], placeholder="Selecione os anos")
    st.session_state.mesesSelecionados = st.sidebar.multiselect(label="Filtrar Meses", options=mesesFiltro, default=[], placeholder="Selecione os meses")
    ## Convertendo os meses selecionados em números
    st.session_state.mesesSelecionadosNumeros = [mesesFiltro.index(mes) + 1 for mes in st.session_state.mesesSelecionados]

    
    # Se não houver anos cadastrados, usar ano atual
    if not anosFiltro:
        from datetime import datetime
        anosFiltro = [datetime.now().year]
    
# Inicializar variáveis de sessão se não existirem
if "mesesSelecionados" not in st.session_state:
    st.session_state.mesesSelecionados = []

if "mesesSelecionadosNumeros" not in st.session_state:
    st.session_state.mesesSelecionadosNumeros = []

if "anosSelecionados" not in st.session_state:
    st.session_state.anosSelecionados = []

# Configuração da página principal
pg = st.navigation({
    "Acesso": [
        st.Page("PaginasStreamlit/st_login.py", title="Login", icon="🔐")
    ],
    "Dashboard": [
        st.Page("PaginasStreamlit/st_paginaInicial.py", title="Página Inicial", icon="🏠")
    ],
    "Cadastros": [
        st.Page("PaginasStreamlit/st_tipoPagamento.py", title="Tipo de Pagamento", icon="📝"),
        st.Page("PaginasStreamlit/st_mesAnoPagamento.py", title="Mês/Ano", icon="📅"),
        st.Page("PaginasStreamlit/st_cadastroPagamento.py", title="Pagamento", icon="💰")
    ],
    "Consultas": [
        st.Page("PaginasStreamlit/st_gestaoPagamentos.py", title="Pagamentos", icon="🔍")
    ]
})

pg.run()
