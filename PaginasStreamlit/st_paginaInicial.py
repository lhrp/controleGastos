from Controller import funcoesTipoPagamento, funcoesMesAnoPagamento, funcoesPagamento
from PaginasStreamlit.middleware_auth import verificar_autenticacao, obter_codigo_usuario, logout
from datetime import datetime, date, timedelta
from types import SimpleNamespace

import streamlit as st
import pandas as pd

# Verificar autenticação
verificar_autenticacao()

# Configurar layout wide
st.set_page_config(layout="wide", page_title="Dashboard - Controle de Gastos")

# Header com nome do usuário e botão de logout
col_header1, col_header2 = st.columns([4, 1])
with col_header1:
    st.header(f"Dashboard")# - Bem-vindo(a), {st.session_state.nomeUsuario}!")
with col_header2:
    if st.button("🚪 Sair"):
        logout()

# Obter código do usuário logado
codigo_usuario = obter_codigo_usuario()

if not codigo_usuario:
    st.error("❌ Erro: Usuário não identificado!")
    st.stop()

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

# Verificar se há dados
if not listaPagamentos:
    st.warning("⚠️ Nenhum pagamento cadastrado ainda!")
    st.info("👉 Cadastre seus primeiros pagamentos para visualizar o dashboard.")
    if st.button("➕ Ir para Cadastro de Pagamentos"):
        st.switch_page("PaginasStreamlit/st_cadastroPagamento.py")
    st.stop()

if not tiposPagamento:
    st.warning("⚠️ Nenhum tipo de pagamento cadastrado!")
    if st.button("➕ Ir para Cadastro de Tipos"):
        st.switch_page("PaginasStreamlit/st_cadastroTipoPagamento.py")
    st.stop()

# Transformar em objetos
pagamentos = [SimpleNamespace(**pag) for pag in listaPagamentos]

# Filtrar pagamentos por mês/ano
pagamentos_filtrados = []

for pag in pagamentos:
    # Buscar informação do mês/ano
    mes_ano_info = funcoesMesAnoPagamento.get("consultarPorCodigo")(pag.codigoMesAnoPagamento, codigo_usuario)
    
    if mes_ano_info and mes_ano_info.get("status") == "SUCESSO":
        mes_pag = mes_ano_info.get("mesPagamento")
        ano_pag = mes_ano_info.get("anoPagamento")
        
        # Verificar se está nos filtros
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

st.info(f"📅 **Período: {periodo_texto}**")

# Se não houver pagamentos filtrados
if not pagamentos_filtrados:
    st.warning("⚠️ Nenhum pagamento encontrado no período selecionado!")
    
    # Mostrar períodos disponíveis
    with st.expander("📊 Ver períodos disponíveis"):
        periodos = {}
        for pag in pagamentos:
            ma = funcoesMesAnoPagamento.get("consultarPorCodigo")(pag.codigoMesAnoPagamento, codigo_usuario)
            if ma and ma.get("status") == "SUCESSO":
                periodo = f"{ma['mesPagamento']:02d}/{ma['anoPagamento']}"
                periodos[periodo] = periodos.get(periodo, 0) + 1
        
        if periodos:
            for p, qtd in sorted(periodos.items()):
                st.write(f"- **{p}**: {qtd} pagamento(s)")
    
    st.stop()

# ============= CÁLCULOS =============
total_receitas = 0
total_receitas_recebidas = 0
total_receitas_pendentes = 0
total_receitas_atrasadas = 0

total_despesas = 0
total_despesas_pagas = 0
total_despesas_pendentes = 0
total_despesas_atrasadas = 0

receitas_detalhadas = []
despesas_detalhadas = []
receitas_atrasadas_lista = []
despesas_atrasadas_lista = []

for pag in pagamentos_filtrados:
    tipo_info = tiposPagamento.get(pag.codigoTipoPagamento, {})
    opcao = tipo_info.get('opcaoTipoPagamento', '')

    valor = float(pag.valorPagamento)
    
    # Verificar se está atrasado
    esta_atrasado = pag.vencimentoPagamento < hoje and not pag.statusPagamento
    dias_atraso = (hoje - pag.vencimentoPagamento).days if esta_atrasado else 0
    
    if opcao == 1:  # Receita
        total_receitas += valor
        
        if pag.statusPagamento:
            total_receitas_recebidas += valor
            print(total_receitas_recebidas)
            status = 'Recebido'
        else:
            total_receitas_pendentes += valor
            if esta_atrasado:
                total_receitas_atrasadas += valor
                status = f'⚠️ Atrasado ({dias_atraso}d)'
                receitas_atrasadas_lista.append({
                    'Descrição': pag.descricaoPagamento,
                    'Valor': valor,
                    'Vencimento': pag.vencimentoPagamento,
                    'Dias Atraso': dias_atraso
                })
            else:
                status = 'A Receber'
        
        receitas_detalhadas.append({
            'Descrição': pag.descricaoPagamento,
            'Valor': valor,
            'Vencimento': pag.vencimentoPagamento,
            'Status': status
        })
    
    elif opcao == 2:  # Despesa
        total_despesas += valor
        
        if pag.statusPagamento:
            total_despesas_pagas += valor
            status = 'Pago'
        else:
            total_despesas_pendentes += valor
            if esta_atrasado:
                total_despesas_atrasadas += valor
                status = f'⚠️ Atrasado ({dias_atraso}d)'
                despesas_atrasadas_lista.append({
                    'Descrição': pag.descricaoPagamento,
                    'Valor': valor,
                    'Vencimento': pag.vencimentoPagamento,
                    'Dias Atraso': dias_atraso
                })
            else:
                status = 'Pendente'
        
        despesas_detalhadas.append({
            'Descrição': pag.descricaoPagamento,
            'Valor': valor,
            'Vencimento': pag.vencimentoPagamento,
            'Status': status
        })

saldo_previsto = total_receitas - total_despesas
saldo_real = total_receitas_recebidas - total_despesas_pagas
pendentes_total = total_receitas_pendentes + total_despesas_pendentes
atrasados_qtd = len(receitas_atrasadas_lista) + len(despesas_atrasadas_lista)

# Alerta de atraso
if atrasados_qtd > 0:
    st.error(f"⚠️ **ATENÇÃO:** {len(receitas_atrasadas_lista)} receita(s) e {len(despesas_atrasadas_lista)} despesa(s) em atraso!")

# ============= CARDS PRINCIPAIS =============
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Total Receitas",
        value=f"R$ {total_receitas:,.2f}",
        delta=f"Recebido: R$ {total_receitas_recebidas:,.2f} | A Receber: R$ {total_receitas_pendentes:,.2f}"
    )

with col2:
    st.metric(
        label="💸 Total Despesas",
        value=f"R$ {total_despesas:,.2f}",
        delta=f"Pago: R$ {total_despesas_pagas:,.2f} | A Pagar: R$ {total_despesas_pendentes:,.2f}"
    )

with col3:
    st.metric(
        label="📊 Saldo Previsto",
        value=f"R$ {saldo_previsto:,.2f}",
        delta=f"Real: R$ {saldo_real:,.2f}",
        delta_color="normal" if saldo_previsto >= 0 else "inverse"
    )

with col4:
    st.metric(
        label="⏳ Pendentes",
        value=f"R$ {pendentes_total:,.2f}",
        delta=f"{atrasados_qtd} atrasado(s)" if atrasados_qtd > 0 else "Tudo em dia"
    )

st.divider()

# ============= CARDS DE ATRASO =============
if receitas_atrasadas_lista or despesas_atrasadas_lista:
    col_at1, col_at2 = st.columns(2)
    
    with col_at1:
        st.metric(
            label="⚠️ Receitas Atrasadas",
            value=f"R$ {total_receitas_atrasadas:,.2f}",
            delta=f"{len(receitas_atrasadas_lista)} item(ns)",
            delta_color="inverse"
        )
    
    with col_at2:
        st.metric(
            label="⚠️ Despesas Atrasadas",
            value=f"R$ {total_despesas_atrasadas:,.2f}",
            delta=f"{len(despesas_atrasadas_lista)} item(ns)",
            delta_color="inverse"
        )
    
    st.divider()

# ============= TABELAS RECEITAS E DESPESAS =============
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📈 Receitas")
    if receitas_detalhadas:
        df_rec = pd.DataFrame(receitas_detalhadas)
        df_rec['Valor'] = df_rec['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_rec['Vencimento'] = pd.to_datetime(df_rec['Vencimento']).dt.strftime("%d/%m/%Y")
        st.dataframe(df_rec, hide_index=True, height=300)
    else:
        st.info("Nenhuma receita registrada no período")

with col_dir:
    st.subheader("📉 Despesas")
    if despesas_detalhadas:
        df_desp = pd.DataFrame(despesas_detalhadas)
        df_desp['Valor'] = df_desp['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_desp['Vencimento'] = pd.to_datetime(df_desp['Vencimento']).dt.strftime("%d/%m/%Y")
        st.dataframe(df_desp, hide_index=True, height=300)
    else:
        st.info("Nenhuma despesa registrada no período")

st.divider()

# ============= ITENS ATRASADOS =============
if receitas_atrasadas_lista or despesas_atrasadas_lista:
    st.subheader("⚠️ Itens em Atraso")
    
    col_at_esq, col_at_dir = st.columns(2)
    
    with col_at_esq:
        if receitas_atrasadas_lista:
            st.markdown("**Receitas Atrasadas**")
            df_rec_at = pd.DataFrame(receitas_atrasadas_lista)
            df_rec_at['Valor'] = df_rec_at['Valor'].apply(lambda x: f"R$ {x:,.2f}")
            df_rec_at['Vencimento'] = pd.to_datetime(df_rec_at['Vencimento']).dt.strftime("%d/%m/%Y")
            st.dataframe(df_rec_at, hide_index=True)
    
    with col_at_dir:
        if despesas_atrasadas_lista:
            st.markdown("**Despesas Atrasadas**")
            df_desp_at = pd.DataFrame(despesas_atrasadas_lista)
            df_desp_at['Valor'] = df_desp_at['Valor'].apply(lambda x: f"R$ {x:,.2f}")
            df_desp_at['Vencimento'] = pd.to_datetime(df_desp_at['Vencimento']).dt.strftime("%d/%m/%Y")
            st.dataframe(df_desp_at, hide_index=True)
    
    st.divider()

# ============= RESUMO POR TIPO =============
st.subheader("📋 Resumo por Tipo de Pagamento")

resumo_tipos = {}
for pag in pagamentos_filtrados:
    tipo_info = tiposPagamento.get(pag.codigoTipoPagamento, {})
    nome_tipo = tipo_info.get('nomeTipoPagamento', 'Desconhecido')
    opcao = tipo_info.get('opcaoTipoPagamento', '')
    valor = float(pag.valorPagamento)
    
    if nome_tipo not in resumo_tipos:
        resumo_tipos[nome_tipo] = {
            'Categoria': 'Receita' if opcao == 1 else 'Despesa',
            'Total (R$)': 0,
            'Qtd': 0,
            'Pagos': 0,
            'Pendentes': 0
        }
    
    resumo_tipos[nome_tipo]['Total (R$)'] += valor
    resumo_tipos[nome_tipo]['Qtd'] += 1
    
    if pag.statusPagamento:
        resumo_tipos[nome_tipo]['Pagos'] += 1
    else:
        resumo_tipos[nome_tipo]['Pendentes'] += 1

if resumo_tipos:
    df_resumo = pd.DataFrame.from_dict(resumo_tipos, orient='index').reset_index()
    df_resumo.columns = ['Nome', 'Categoria', 'Total (R$)', 'Qtd', 'Pagos', 'Pendentes']
    df_resumo['Total (R$)'] = df_resumo['Total (R$)'].apply(lambda x: f"R$ {x:,.2f}")
    st.dataframe(df_resumo, hide_index=True, height=300)

st.divider()

# ============= VENCIMENTOS PRÓXIMOS =============
st.subheader("⏰ Vencimentos Próximos (7 dias)")
data_limite = hoje + timedelta(days=7)

vencimentos = []
for pag in pagamentos_filtrados:
    if not pag.statusPagamento and hoje <= pag.vencimentoPagamento <= data_limite:
        tipo_info = tiposPagamento.get(pag.codigoTipoPagamento, {})
        dias_rest = (pag.vencimentoPagamento - hoje).days
        categoria = 'Receita' if tipo_info.get('opcaoTipoPagamento') == 1 else 'Despesa'
        
        vencimentos.append({
            'Descrição': pag.descricaoPagamento,
            'Categoria': categoria,
            'Valor': f"R$ {pag.valorPagamento:,.2f}",
            'Vencimento': pag.vencimentoPagamento.strftime("%d/%m/%Y"),
            'Dias Restantes': dias_rest
        })

if vencimentos:
    df_venc = pd.DataFrame(vencimentos).sort_values('Dias Restantes')
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown("**💰 Receitas a Vencer**")
        df_rec_venc = df_venc[df_venc['Categoria'] == 'Receita']
        if not df_rec_venc.empty:
            st.dataframe(df_rec_venc.drop('Categoria', axis=1), hide_index=True)
        else:
            st.info("Nenhuma receita próxima")
    
    with col_v2:
        st.markdown("**💸 Despesas a Vencer**")
        df_desp_venc = df_venc[df_venc['Categoria'] == 'Despesa']
        if not df_desp_venc.empty:
            st.dataframe(df_desp_venc.drop('Categoria', axis=1), hide_index=True)
        else:
            st.info("Nenhuma despesa próxima")
else:
    st.success("✅ Nenhum vencimento nos próximos 7 dias!")