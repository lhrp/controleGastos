from Controller import funcoesUsuario
import streamlit as st

st.set_page_config(page_title="Login - Controle de Gastos", layout="centered")

# Verificar se já está logado
if 'usuario_logado' in st.session_state and st.session_state.usuario_logado:
    st.switch_page("PaginasStreamlit/st_paginaInicial.py")

st.title("🔐 Controle de Gastos")
st.markdown("### Sistema de Gestão Financeira")

# Tabs para Login e Cadastro
tab_login, tab_cadastro = st.tabs(["Login", "Criar Conta"])

# TAB LOGIN
with tab_login:
    st.subheader("Acesse sua conta")
    
    with st.form("form_login"):
        email_login = st.text_input("Email", key="email_login")
        senha_login = st.text_input("Senha", type="password", key="senha_login")
        
        col1, col2 = st.columns(2)
        with col1:
            btn_login = st.form_submit_button("🔓 Entrar", width="stretch", type="primary")
        with col2:
            btn_esqueci_senha = st.form_submit_button("❓ Esqueci minha senha", width="stretch")
        
        if btn_login:
            if not email_login or not senha_login:
                st.error("Preencha todos os campos!")
            else:
                resultado = funcoesUsuario.get("autenticar")(email_login, senha_login)
                
                if resultado.get("status") == "SUCESSO":
                    # Salvar dados do usuário na sessão
                    st.session_state.usuario_logado = True
                    st.session_state.codigoUsuario = resultado.get("codigoUsuario")
                    st.session_state.nomeUsuario = resultado.get("nomeUsuario")
                    st.session_state.emailUsuario = resultado.get("emailUsuario")
                    
                    st.success(f"Bem-vindo(a), {resultado.get('nomeUsuario')}!")
                    st.rerun()
                else:
                    st.error(resultado.get("mensagem"))
        
        if btn_esqueci_senha:
            st.info("Em desenvolvimento. Entre em contato com o suporte.")

# TAB CADASTRO
with tab_cadastro:
    st.subheader("Criar nova conta")
    
    with st.form("form_cadastro"):
        nome_cadastro = st.text_input("Nome Completo", key="nome_cadastro")
        email_cadastro = st.text_input("Email", key="email_cadastro")
        senha_cadastro = st.text_input("Senha (mín. 6 caracteres)", type="password", key="senha_cadastro")
        senha_confirma = st.text_input("Confirmar Senha", type="password", key="senha_confirma")
        
        aceite_termos = st.checkbox("Aceito os termos de uso e política de privacidade")
        
        btn_cadastrar = st.form_submit_button("📝 Criar Conta", width="stretch", type="primary")
        
        if btn_cadastrar:
            if not all([nome_cadastro, email_cadastro, senha_cadastro, senha_confirma]):
                st.error("Preencha todos os campos!")
            elif senha_cadastro != senha_confirma:
                st.error("As senhas não coincidem!")
            elif not aceite_termos:
                st.error("Você precisa aceitar os termos de uso!")
            else:
                resultado = funcoesUsuario.get("cadastrar")(
                    nomeUsuario=nome_cadastro,
                    emailUsuario=email_cadastro,
                    senhaUsuario=senha_cadastro
                )
                
                if resultado.get("status") == "SUCESSO":
                    st.success(resultado.get("mensagem"))
                    st.info("Agora você pode fazer login com suas credenciais!")
                else:
                    st.error(resultado.get("mensagem"))

st.markdown("---")
st.markdown("© 2025 Controle de Gastos - Todos os direitos reservados")