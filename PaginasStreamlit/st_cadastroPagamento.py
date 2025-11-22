from Controller import funcoesTipoPagamento, funcoesPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario
from datetime import datetime
import streamlit as st

# Verificar autenticação
verificar_autenticacao()

st.set_page_config(page_title="Cadastro Pagamento", layout="centered")

st.title("Cadastro de Pagamento")

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

# Obter tipos de pagamento do usuário
tiposPagamento = funcoesTipoPagamento.get("listar")(codigo_usuario)

if not tiposPagamento:
    st.warning("⚠️ Você precisa cadastrar pelo menos um tipo de pagamento antes de cadastrar pagamentos!")
    if st.button("➕ Cadastrar Tipo de Pagamento"):
        st.switch_page("PaginasStreamlit/st_cadastroTipoPagamento.py")
    st.stop()

# Formulário de cadastro
descricaoPagamento = st.text_input("Descrição do Pagamento", max_chars=100)

# Selectbox de tipos
opcoes_tipos = {tp['codigoTipoPagamento']: f"{tp['nomeTipoPagamento']} ({'Receita' if tp['opcaoTipoPagamento'] == '1-Entrada' else 'Despesa'})" 
                for tp in tiposPagamento}

codigoTipoPagamento = st.selectbox(
    "Tipo de Pagamento",
    options=list(opcoes_tipos.keys()),
    format_func=lambda x: opcoes_tipos[x]
)

valorPagamento = st.number_input("Valor do Pagamento (R$)", min_value=0.01, value=100.00, step=0.01, format="%.2f")

vencimentoPagamento = st.date_input(
    label="Data de Vencimento do Pagamento", 
    format="DD/MM/YYYY",
    value=datetime.now().date()
)

statusPagamento = st.checkbox("Pagamento já foi realizado?", value=False)

# Campos adicionais para pagamento parcelado
numeroParcelas = 1
valorTotalParcelado = 1

if codigoTipoPagamento == 4:  # Se for tipo Parcelado
    st.markdown("---")
    st.markdown("**Configurações de Parcelamento**")
    numeroParcelas = st.number_input("Número de Parcelas", min_value=1, max_value=120, value=1, step=1)
    valorTotalParcelado = st.radio(
        "O valor informado é:",
        options=[1, 2],
        format_func=lambda x: "Valor Total" if x == 1 else "Valor da Parcela",
        horizontal=True
    )

st.divider()

# Botões
col1, col2 = st.columns(2)

with col1:
    btn_cadastrar = st.button("💾 Cadastrar", width="stretch", type="primary")

with col2:
    btn_limpar = st.button("🔄 Limpar", width="stretch")

if btn_cadastrar:
    if not descricaoPagamento:
        st.error("Preencha a descrição do pagamento!")
    else:
        # Se for parcelado (tipo 4)
        if codigoTipoPagamento == 4 and numeroParcelas > 1:
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            
            # Calcular valor da parcela
            if valorTotalParcelado == 1:  # Valor total informado
                valor_parcela = valorPagamento / numeroParcelas
            else:  # Valor da parcela informado
                valor_parcela = valorPagamento
            
            sucessos = 0
            erros = 0
            
            # Cadastrar cada parcela
            for i in range(numeroParcelas):
                data_vencimento = vencimentoPagamento + relativedelta(months=i)
                
                resultado = funcoesPagamento.get("cadastrar")(
                    codigoUsuario=codigo_usuario,
                    descricaoPagamento=f"{descricaoPagamento} - Parcela {i+1}/{numeroParcelas}",
                    codigoTipoPagamento=codigoTipoPagamento,
                    valorPagamento=valor_parcela,
                    vencimentoPagamento=data_vencimento,
                    numeroParcelaPagamento=i+1,
                    statusPagamento=statusPagamento if i == 0 else False
                )
                
                if resultado.get("status") == "SUCESSO":
                    sucessos += 1
                else:
                    erros += 1
            
            if sucessos > 0:
                st.success(f"✅ {sucessos} parcela(s) cadastrada(s) com sucesso!")
            if erros > 0:
                st.error(f"❌ {erros} parcela(s) com erro!")
        
        else:
            # Cadastro normal
            resultado = funcoesPagamento.get("cadastrar")(
                codigoUsuario=codigo_usuario,
                descricaoPagamento=descricaoPagamento,
                codigoTipoPagamento=codigoTipoPagamento,
                valorPagamento=valorPagamento,
                vencimentoPagamento=vencimentoPagamento,
                numeroParcelaPagamento=1,
                statusPagamento=statusPagamento
            )
            
            if resultado.get("status") == "SUCESSO":
                st.success(resultado.get("mensagem"))
                
                # Se for tipo fixo (código 2), mostrar quantos foram cadastrados
                if codigoTipoPagamento == 2:
                    resultados_fixo = resultado.get("resultados", [])
                    sucessos_fixo = len([r for r in resultados_fixo if r.get("status") == "SUCESSO"])
                    st.info(f"📅 Pagamento fixo criado para {sucessos_fixo} mês(es)!")
            else:
                st.error(resultado.get("mensagem"))

if btn_limpar:
    st.rerun()

st.divider()

# Listar últimos pagamentos do usuário
st.subheader("💳 Meus Últimos Pagamentos")

pagamentos = funcoesPagamento.get("listar")(codigo_usuario)

if pagamentos:
    import pandas as pd
    
    # Pegar apenas os 10 últimos
    ultimos_pagamentos = pagamentos[:10]
    
    dados_exibicao = []
    for pag in ultimos_pagamentos:
        tipo = next((t for t in tiposPagamento if t['codigoTipoPagamento'] == pag['codigoTipoPagamento']), None)
        
        dados_exibicao.append({
            'Descrição': pag['descricaoPagamento'],
            'Tipo': tipo['nomeTipoPagamento'] if tipo else 'N/A',
            'Valor': f"R$ {pag['valorPagamento']:,.2f}",
            'Vencimento': pag['vencimentoPagamento'].strftime("%d/%m/%Y"),
            'Status': '✅ Pago' if pag['statusPagamento'] else '⏳ Pendente'
        })
    
    df = pd.DataFrame(dados_exibicao)
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("Nenhum pagamento cadastrado ainda.")