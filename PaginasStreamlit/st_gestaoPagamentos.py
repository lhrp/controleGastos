from Controller import funcoesTipoPagamento, funcoesMesAnoPagamento, funcoesPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario
from datetime import datetime, date
from types import SimpleNamespace

import streamlit as st
import pandas as pd

# Verificar autenticação
verificar_autenticacao()

st.set_page_config(layout="wide", page_title="Consulta de Pagamentos")

st.title("🔍 Consulta de Pagamentos")

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

# Obter filtros da sessão
mesesFiltrados = st.session_state.get('mesesSelecionadosNumeros', [])
anosFiltrados = st.session_state.get('anosSelecionados', [])

# Se não houver filtros, usar mês e ano atual
hoje = date.today()
if not mesesFiltrados:
    mesesFiltrados = [hoje.month]
if not anosFiltrados:
    anosFiltrados = [hoje.year]

# Obter dados do usuário
listaPagamentos = funcoesPagamento.get("listar")(codigo_usuario)
tiposPagamento = {tp['codigoTipoPagamento']: tp for tp in funcoesTipoPagamento.get("listar")(codigo_usuario)}
mesesAnos = {ma['codigoMesAnoPagamento']: ma for ma in funcoesMesAnoPagamento.get("listar")(codigo_usuario)}

if not listaPagamentos:
    st.warning("⚠️ Nenhum pagamento cadastrado ainda!")
    if st.button("➕ Cadastrar Primeiro Pagamento"):
        st.switch_page("PaginasStreamlit/st_cadastroPagamento.py")
    st.stop()

# Transformar em objetos
pagamentos = [SimpleNamespace(**pag) for pag in listaPagamentos]

# Filtrar pagamentos
pagamentos_filtrados = []

for pag in pagamentos:
    mes_ano_info = mesesAnos.get(pag.codigoMesAnoPagamento, {})
    mes_pag = mes_ano_info.get("mesPagamento")
    ano_pag = mes_ano_info.get("anoPagamento")
    
    if mes_pag in mesesFiltrados and ano_pag in anosFiltrados:
        pagamentos_filtrados.append(pag)

# Exibir período
meses_nomes = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
               7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

if len(mesesFiltrados) == 1 and len(anosFiltrados) == 1:
    periodo_texto = f"{meses_nomes[mesesFiltrados[0]]}/{anosFiltrados[0]}"
else:
    meses_texto = ', '.join([meses_nomes[m] for m in sorted(mesesFiltrados)])
    anos_texto = ', '.join(map(str, sorted(anosFiltrados)))
    periodo_texto = f"{meses_texto} / {anos_texto}"

st.info(f"📅 **Período:** {periodo_texto} | **Total:** {len(pagamentos_filtrados)} pagamento(s)")

if not pagamentos_filtrados:
    st.warning("⚠️ Nenhum pagamento encontrado no período selecionado!")
    st.stop()

# ============= TABELA DE PAGAMENTOS =============
st.subheader("📋 Lista de Pagamentos")

dados_tabela = []
for pag in pagamentos_filtrados:
    tipo_info = tiposPagamento.get(pag.codigoTipoPagamento, {})
    mes_ano_info = mesesAnos.get(pag.codigoMesAnoPagamento, {})
    
    # Calcular status
    if pag.statusPagamento:
        status = '✅ Pago'
    elif pag.vencimentoPagamento < hoje:
        dias_atraso = (hoje - pag.vencimentoPagamento).days
        status = f'⚠️ Atrasado ({dias_atraso}d)'
    else:
        status = '⏳ Pendente'
    
    categoria = 'Receita' if tipo_info.get('opcaoTipoPagamento') == "1-Entrada" else 'Despesa'
    
    dados_tabela.append({
        'Código': pag.codigoPagamento,
        'Descrição': pag.descricaoPagamento,
        'Tipo': tipo_info.get('nomeTipoPagamento', 'N/A'),
        'Categoria': categoria,
        'Valor': f"R$ {pag.valorPagamento:,.2f}",
        'Vencimento': pag.vencimentoPagamento.strftime("%d/%m/%Y"),
        'Parcela': f"{pag.numeroParcelaPagamento}",
        'Mês/Ano': f"{mes_ano_info.get('mesPagamento', 0):02d}/{mes_ano_info.get('anoPagamento', 0)}",
        'Status': status
    })

if dados_tabela:
    df = pd.DataFrame(dados_tabela)
    st.dataframe(df, hide_index=True, height=400)

st.divider()

# ============= ESTATÍSTICAS RÁPIDAS =============
col1, col2, col3, col4 = st.columns(4)

total_receitas = sum(float(pag.valorPagamento) for pag in pagamentos_filtrados 
                     if tiposPagamento.get(pag.codigoTipoPagamento, {}).get('opcaoTipoPagamento') == 1)

total_despesas = sum(float(pag.valorPagamento) for pag in pagamentos_filtrados 
                     if tiposPagamento.get(pag.codigoTipoPagamento, {}).get('opcaoTipoPagamento') == 2)

qtd_pagos = sum(1 for pag in pagamentos_filtrados if pag.statusPagamento)
qtd_pendentes = len(pagamentos_filtrados) - qtd_pagos

with col1:
    st.metric("💰 Receitas", f"R$ {total_receitas:,.2f}")

with col2:
    st.metric("💸 Despesas", f"R$ {total_despesas:,.2f}")

with col3:
    st.metric("✅ Pagos", qtd_pagos)

with col4:
    st.metric("⏳ Pendentes", qtd_pendentes)

st.divider()

# ============= SEÇÃO DE EDIÇÃO =============
st.subheader("✏️ Editar Pagamento")

col_edit1, col_edit2 = st.columns([2, 3])

with col_edit1:
    codigo_editar = st.number_input(
        "🔢 Código do Pagamento",
        min_value=1,
        step=1,
        value=None,
        help="Informe o código do pagamento que deseja editar"
    )
    
    btn_buscar = st.button("🔍 Buscar Pagamento", use_container_width=True, type="primary")

with col_edit2:
    if btn_buscar and codigo_editar:
        # Buscar pagamento
        resultado = funcoesPagamento.get("consultarPagamentoPorCodigo")(codigo_editar, codigo_usuario)
        
        if resultado.get("status") == "SUCESSO":
            st.session_state.pagamento_edicao = resultado
            st.success(f"✅ Pagamento '{resultado['descricaoPagamento']}' encontrado!")
            st.rerun()
        else:
            st.error("❌ Pagamento não encontrado ou não pertence ao seu usuário!")
            if 'pagamento_edicao' in st.session_state:
                del st.session_state.pagamento_edicao

# ============= FORMULÁRIO DE EDIÇÃO =============
if 'pagamento_edicao' in st.session_state:
    st.divider()
    
    pag_edit = st.session_state.pagamento_edicao
    
    st.info(f"📝 Editando pagamento: **{pag_edit['descricaoPagamento']}** (Código: {pag_edit['codigoPagamento']})")
    
    with st.form("form_editar_pagamento"):
        col_form1, col_form2, col_form3 = st.columns(3)
        
        with col_form1:
            descricao_edit = st.text_input(
                "📝 Descrição*",
                value=pag_edit['descricaoPagamento'],
                max_chars=100
            )
            
            # Buscar tipo atual
            tipo_atual = tiposPagamento.get(pag_edit['codigoTipoPagamento'], {})
            tipos_opcoes = [(tp['codigoTipoPagamento'], f"{tp['nomeTipoPagamento']} ({tp['opcaoTipoPagamento']})") 
                           for tp in funcoesTipoPagamento.get("listar")(codigo_usuario)]
            
            tipo_index = next((i for i, (cod, _) in enumerate(tipos_opcoes) 
                              if cod == pag_edit['codigoTipoPagamento']), 0)
            
            tipo_edit = st.selectbox(
                "🏷️ Tipo de Pagamento*",
                options=[cod for cod, _ in tipos_opcoes],
                format_func=lambda x: next(nome for cod, nome in tipos_opcoes if cod == x),
                index=tipo_index
            )
            
            valor_edit = st.number_input(
                "💵 Valor*",
                min_value=0.01,
                value=float(pag_edit['valorPagamento']),
                step=0.01,
                format="%.2f"
            )
        
        with col_form2:
            # Converter string de data para objeto date
            vencimento_atual = datetime.strptime(pag_edit['vencimentoPagamento'], "%Y-%m-%d").date()
            
            vencimento_edit = st.date_input(
                "📅 Data de Vencimento*",
                value=vencimento_atual,
                format="DD/MM/YYYY"
            )
            
            status_edit = st.checkbox(
                "✅ Pagamento Realizado",
                value=pag_edit['statusPagamento']
            )
            
            # Buscar mês/ano atual
            mes_ano_atual_info = mesesAnos.get(pag_edit['codigoMesAnoPagamento'], {})
            mes_ano_texto = f"{mes_ano_atual_info.get('mesPagamento', 0):02d}/{mes_ano_atual_info.get('anoPagamento', 0)}"
            
            meses_anos_opcoes = [(ma['codigoMesAnoPagamento'], 
                                 f"{ma['mesPagamento']:02d}/{ma['anoPagamento']}") 
                                for ma in funcoesMesAnoPagamento.get("listar")(codigo_usuario)]
            
            mes_ano_index = next((i for i, (cod, _) in enumerate(meses_anos_opcoes) 
                                 if cod == pag_edit['codigoMesAnoPagamento']), 0)
            
            mes_ano_edit = st.selectbox(
                "📆 Mês/Ano de Referência*",
                options=[cod for cod, _ in meses_anos_opcoes],
                format_func=lambda x: next(texto for cod, texto in meses_anos_opcoes if cod == x),
                index=mes_ano_index
            )
        
        with col_form3:
            parcela_edit = st.number_input(
                "🔢 Número da Parcela",
                min_value=1,
                value=pag_edit['numeroParcelaPagamento'],
                step=1
            )
            
    
            
            observacoes_edit = st.text_area(
                "📄 Observações",
                value=pag_edit.get('observacoesPagamento', '') or '',
                max_chars=500,
                height=100
            )
        
        st.divider()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            btn_salvar = st.form_submit_button(
                "💾 Salvar Alterações",
                use_container_width=True,
                type="primary"
            )
        
        with col_btn2:
            btn_cancelar = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        with col_btn3:
            btn_excluir = st.form_submit_button(
                "🗑️ Excluir Pagamento",
                use_container_width=True,
                type="secondary"
            )
        
        # Processar ações
        if btn_salvar:
            if not descricao_edit or not tipo_edit or not mes_ano_edit:
                st.error("❌ Preencha todos os campos obrigatórios!")
            else:
                resultado = funcoesPagamento.get("atualizar")(
                    codigoPagamento=pag_edit['codigoPagamento'],
                    codigoUsuario=codigo_usuario,
                    descricaoPagamento=descricao_edit,
                    codigoTipoPagamento=tipo_edit,
                    valorPagamento=valor_edit,
                    vencimentoPagamento=vencimento_edit,
                    statusPagamento=status_edit,
                    codigoMesAnoPagamento=mes_ano_edit,
                    numeroParcelaPagamento=parcela_edit,
                    observacoesPagamento=observacoes_edit if observacoes_edit else None
                )
                
                if resultado.get("status") == "SUCESSO":
                    st.success("✅ Pagamento atualizado com sucesso!")
                    del st.session_state.pagamento_edicao
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {resultado.get('mensagem', 'Erro ao atualizar')}")
        
        if btn_cancelar:
            del st.session_state.pagamento_edicao
            st.info("ℹ️ Edição cancelada")
            st.rerun()
        
        if btn_excluir:
            st.session_state.confirmar_exclusao = True
            st.rerun()

# ============= CONFIRMAÇÃO DE EXCLUSÃO =============
if 'confirmar_exclusao' in st.session_state and st.session_state.confirmar_exclusao:
    st.divider()
    st.error("⚠️ **ATENÇÃO: Esta ação não pode ser desfeita!**")
    
    col_conf1, col_conf2 = st.columns(2)
    
    with col_conf1:
        if st.button("✅ Sim, excluir pagamento", use_container_width=True, type="primary"):
            resultado = funcoesPagamento.get("remover")(
                st.session_state.pagamento_edicao['codigoPagamento'],
                codigo_usuario
            )
            
            if resultado.get("status") == "SUCESSO":
                st.success("✅ Pagamento excluído com sucesso!")
                del st.session_state.pagamento_edicao
                del st.session_state.confirmar_exclusao
                st.rerun()
            else:
                st.error(f"❌ {resultado.get('mensagem', 'Erro ao excluir')}")
    
    with col_conf2:
        if st.button("❌ Não, cancelar", use_container_width=True):
            del st.session_state.confirmar_exclusao
            st.rerun()


