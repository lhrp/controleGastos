from Controller import funcoesTipoPagamento, funcoesMesAnoPagamento, funcoesPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario
from datetime import datetime
import streamlit as st
import pandas as pd

# Verificar autenticação
verificar_autenticacao()

st.set_page_config(page_title="Consulta Pagamentos", layout="wide")

st.title("Consulta e Gerenciamento de Pagamentos")

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

# Obter dados do usuário
pagamentos = funcoesPagamento.get("listar")(codigo_usuario)
tiposPagamento = {tp['codigoTipoPagamento']: tp for tp in funcoesTipoPagamento.get("listar")(codigo_usuario)}
mesesAnos = funcoesMesAnoPagamento.get("listar")(codigo_usuario)

if not pagamentos:
    st.info("📭 Você ainda não tem pagamentos cadastrados.")
    if st.button("➕ Cadastrar Primeiro Pagamento"):
        st.switch_page("PaginasStreamlit/st_cadastroPagamento.py")
    st.stop()

# Filtros
st.subheader("🔍 Filtros")

col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

with col_filtro1:
    filtro_descricao = st.text_input("Buscar por descrição")

with col_filtro2:
    opcoes_tipo = {0: "Todos"} | {tp['codigoTipoPagamento']: tp['nomeTipoPagamento'] for tp in tiposPagamento.values()}
    filtro_tipo = st.selectbox(
        "Tipo de Pagamento",
        options=list(opcoes_tipo.keys()),
        format_func=lambda x: opcoes_tipo[x]
    )

with col_filtro3:
    filtro_status = st.selectbox(
        "Status",
        options=["Todos", "Pago", "Pendente"]
    )

with col_filtro4:
    opcoes_mes_ano = {0: "Todos"} | {ma['codigoMesAnoPagamento']: f"{ma['mesPagamento']:02d}/{ma['anoPagamento']}" 
                                     for ma in mesesAnos}
    filtro_mes_ano = st.selectbox(
        "Mês/Ano",
        options=list(opcoes_mes_ano.keys()),
        format_func=lambda x: opcoes_mes_ano[x]
    )

# Aplicar filtros
pagamentos_filtrados = pagamentos.copy()

if filtro_descricao:
    pagamentos_filtrados = [p for p in pagamentos_filtrados 
                           if filtro_descricao.lower() in p['descricaoPagamento'].lower()]

if filtro_tipo != 0:
    pagamentos_filtrados = [p for p in pagamentos_filtrados 
                           if p['codigoTipoPagamento'] == filtro_tipo]

if filtro_status != "Todos":
    status_bool = filtro_status == "Pago"
    pagamentos_filtrados = [p for p in pagamentos_filtrados 
                           if p['statusPagamento'] == status_bool]

if filtro_mes_ano != 0:
    pagamentos_filtrados = [p for p in pagamentos_filtrados 
                           if p['codigoMesAnoPagamento'] == filtro_mes_ano]

st.divider()

# Estatísticas
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

total_geral = sum(p['valorPagamento'] for p in pagamentos_filtrados)
total_pago = sum(p['valorPagamento'] for p in pagamentos_filtrados if p['statusPagamento'])
total_pendente = sum(p['valorPagamento'] for p in pagamentos_filtrados if not p['statusPagamento'])
quantidade = len(pagamentos_filtrados)

with col_stat1:
    st.metric("💰 Total", f"R$ {total_geral:,.2f}")

with col_stat2:
    st.metric("✅ Pago", f"R$ {total_pago:,.2f}")

with col_stat3:
    st.metric("⏳ Pendente", f"R$ {total_pendente:,.2f}")

with col_stat4:
    st.metric("📊 Quantidade", quantidade)

st.divider()

# Tabela de pagamentos
st.subheader(f"📋 Pagamentos Encontrados: {quantidade}")

if pagamentos_filtrados:
    dados_tabela = []
    
    for pag in pagamentos_filtrados:
        tipo = tiposPagamento.get(pag['codigoTipoPagamento'], {})
        mes_ano = next((ma for ma in mesesAnos if ma['codigoMesAnoPagamento'] == pag['codigoMesAnoPagamento']), {})
        
        dados_tabela.append({
            'Código': pag['codigoPagamento'],
            'Descrição': pag['descricaoPagamento'],
            'Tipo': tipo.get('nomeTipoPagamento', 'N/A'),
            'Categoria': 'Receita' if tipo.get('opcaoTipoPagamento') == "1-Entrada" else 'Despesa',
            'Valor': f"R$ {pag['valorPagamento']:,.2f}",
            'Vencimento': pag['vencimentoPagamento'].strftime("%d/%m/%Y"),
            'Mês/Ano': f"{mes_ano.get('mesPagamento', 0):02d}/{mes_ano.get('anoPagamento', 0)}",
            'Parcela': pag['numeroParcelaPagamento'],
            'Status': '✅ Pago' if pag['statusPagamento'] else '⏳ Pendente'
        })
    
    df = pd.DataFrame(dados_tabela)
    
    # Usar data_editor para permitir seleção
    df_selecionado = st.data_editor(
        df,
        width="stretch",
        hide_index=True,
        disabled=list(df.columns),
        key="tabela_pagamentos"
    )
    
    st.divider()
    
    # Ações em lote
    st.subheader("⚙️ Ações")
    
    col_acao1, col_acao2, col_acao3, col_acao4 = st.columns(4)
    
    with col_acao1:
        codigo_acao = st.number_input("Código do Pagamento", min_value=1, step=1, key="cod_acao")
    
    with col_acao2:
        if st.button("✅ Marcar como Pago", width="stretch"):
            if codigo_acao:
                resultado = funcoesPagamento.get("atualizar")(
                    codigoPagamento=codigo_acao,
                    codigoUsuario=codigo_usuario,
                    statusPagamento=True
                )
                
                if resultado.get("status") == "SUCESSO":
                    st.success("Pagamento marcado como pago!")
                    st.rerun()
                else:
                    st.error(resultado.get("mensagem"))
    
    with col_acao3:
        if st.button("⏳ Marcar como Pendente", width="stretch"):
            if codigo_acao:
                resultado = funcoesPagamento.get("atualizar")(
                    codigoPagamento=codigo_acao,
                    codigoUsuario=codigo_usuario,
                    statusPagamento=False
                )
                
                if resultado.get("status") == "SUCESSO":
                    st.success("Pagamento marcado como pendente!")
                    st.rerun()
                else:
                    st.error(resultado.get("mensagem"))
    
    with col_acao4:
        if st.button("🗑️ Remover", width="stretch", type="secondary"):
            if codigo_acao:
                if st.session_state.get('confirmar_exclusao') != codigo_acao:
                    st.session_state.confirmar_exclusao = codigo_acao
                    st.warning("⚠️ Clique novamente para confirmar a exclusão!")
                else:
                    resultado = funcoesPagamento.get("remover")(
                        codigoPagamento=codigo_acao,
                        codigoUsuario=codigo_usuario
                    )
                    
                    if resultado.get("status") == "SUCESSO":
                        st.success("Pagamento removido!")
                        st.session_state.confirmar_exclusao = None
                        st.rerun()
                    else:
                        st.error(resultado.get("mensagem"))

else:
    st.info("Nenhum pagamento encontrado com os filtros aplicados.")


