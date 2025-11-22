from Controller import funcoesTipoPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario
import streamlit as st
import pandas as pd

# Verificar autenticação
verificar_autenticacao()

st.set_page_config(page_title="Cadastro Tipo de Pagamento", layout="centered")

st.title("Cadastro de Tipo de Pagamento")

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

with st.form("form_tipo_pagamento"):
    nomeTipoPagamento = st.text_input("Nome do Tipo de Pagamento", max_chars=50)
    opcaoTipoPagamento = st.selectbox(
        "Opção",
        options=["1-Entrada", "2-Saída"],
        format_func=lambda x: "Receita" if x == "1-Entrada" else "Despesa"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        btn_cadastrar = st.form_submit_button("💾 Cadastrar", width="stretch", type="primary")
    with col2:
        btn_limpar = st.form_submit_button("🔄 Limpar", width="stretch")
    
    if btn_cadastrar:
        if not nomeTipoPagamento:
            st.error("Preencha o nome do tipo de pagamento!")
        else:
            resultado = funcoesTipoPagamento.get("cadastrar")(
                codigoUsuario=codigo_usuario,
                nomeTipoPagamento=nomeTipoPagamento,
                opcaoTipoPagamento=opcaoTipoPagamento
            )
            
            if resultado.get("status") == "SUCESSO":
                st.success(resultado.get("mensagem"))
            else:
                st.error(resultado.get("mensagem"))
    
    if btn_limpar:
        st.rerun()

st.divider()

# Listar tipos de pagamento do usuário
st.subheader("📋 Meus Tipos de Pagamento")

tipos = funcoesTipoPagamento.get("listar")(codigo_usuario)

if tipos:
    df_tipos = pd.DataFrame(tipos)
    df_tipos['Categoria'] = df_tipos['opcaoTipoPagamento'].apply(
        lambda x: "Receita" if x == "1-Entrada" else "Despesa"
    )
    df_tipos = df_tipos[['codigoTipoPagamento', 'nomeTipoPagamento', 'Categoria']]
    df_tipos.columns = ['Código', 'Nome', 'Categoria']
    
    st.dataframe(df_tipos, width="stretch", hide_index=True)
else:
    st.info("Nenhum tipo de pagamento cadastrado ainda.")