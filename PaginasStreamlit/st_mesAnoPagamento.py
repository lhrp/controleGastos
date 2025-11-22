from Controller import funcoesMesAnoPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario
import streamlit as st
import pandas as pd

# Verificar autenticação
verificar_autenticacao()

st.set_page_config(page_title="Cadastro Mês/Ano", layout="centered")

st.title("Cadastro de Mês/Ano para Pagamentos")

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

with st.form("form_mes_ano"):
    col1, col2 = st.columns(2)
    
    with col1:
        mesPagamento = st.selectbox(
            "Mês",
            options=list(range(1, 13)),
            format_func=lambda x: f"{x:02d}"
        )
    
    with col2:
        anoPagamento = st.number_input(
            "Ano",
            min_value=2020,
            max_value=2050,
            value=2025,
            step=1
        )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_cadastrar = st.form_submit_button("💾 Cadastrar", width="stretch", type="primary")
    with col_btn2:
        btn_limpar = st.form_submit_button("🔄 Limpar", width="stretch")
    
    if btn_cadastrar:
        resultado = funcoesMesAnoPagamento.get("cadastrar")(
            codigoUsuario=codigo_usuario,
            mesPagamento=mesPagamento,
            anoPagamento=anoPagamento
        )
        
        if resultado.get("status") == "SUCESSO":
            st.success(resultado.get("mensagem"))
        else:
            st.error(resultado.get("mensagem"))
    
    if btn_limpar:
        st.rerun()

st.divider()

# Listar meses/anos do usuário
st.subheader("📅 Meus Meses/Anos Cadastrados")

meses_anos = funcoesMesAnoPagamento.get("listar")(codigo_usuario)

if meses_anos:
    df_meses = pd.DataFrame(meses_anos)
    df_meses['Período'] = df_meses.apply(
        lambda x: f"{x['mesPagamento']:02d}/{x['anoPagamento']}", 
        axis=1
    )
    df_meses = df_meses[['codigoMesAnoPagamento', 'Período']]
    df_meses.columns = ['Código', 'Mês/Ano']
    
    st.dataframe(df_meses, width="stretch", hide_index=True)
else:
    st.info("Nenhum mês/ano cadastrado ainda.")

# Botão para cadastrar múltiplos meses
st.divider()
st.subheader("⚡ Cadastro Rápido")

with st.form("form_rapido"):
    st.write("Cadastre vários meses de uma vez:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ano_rapido = st.number_input("Ano", min_value=2020, max_value=2050, value=2025, step=1, key="ano_rapido")
    
    with col2:
        mes_inicio = st.selectbox("Mês Início", options=list(range(1, 13)), format_func=lambda x: f"{x:02d}", key="mes_inicio")
    
    with col3:
        mes_fim = st.selectbox("Mês Fim", options=list(range(1, 13)), index=11, format_func=lambda x: f"{x:02d}", key="mes_fim")
    
    btn_cadastrar_rapido = st.form_submit_button("💾 Cadastrar Período", width="stretch", type="primary")
    
    if btn_cadastrar_rapido:
        if mes_inicio > mes_fim:
            st.error("Mês inicial deve ser menor ou igual ao mês final!")
        else:
            sucessos = 0
            erros = 0
            
            for mes in range(mes_inicio, mes_fim + 1):

                resultado = funcoesMesAnoPagamento.get("cadastrar")(
                    codigoUsuario=codigo_usuario,
                    mesPagamento=mes,
                    anoPagamento=ano_rapido
                )
                
                if resultado.get("status") == "SUCESSO":
                    sucessos += 1
                else:
                    erros += 1
            
            if sucessos > 0:
                st.success(f"✅ {sucessos} mês(es) cadastrado(s) com sucesso!")
            if erros > 0:
                st.warning(f"⚠️ {erros} mês(es) já existiam ou tiveram erro.")
            
            