import streamlit as st

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    if 'usuario_logado' not in st.session_state or not st.session_state.usuario_logado:
        st.error("⛔ Você precisa fazer login para acessar esta página!")
        st.info("Redirecionando para a página de login...")
        st.switch_page("PaginasStreamlit/st_login.py")
        st.stop()

def obter_codigo_usuario():
    """Retorna o código do usuário logado"""
    if 'codigoUsuario' in st.session_state:
        return st.session_state.codigoUsuario
    return None

def logout():
    """Realiza o logout do usuário"""
    st.session_state.clear()
    st.success("Logout realizado com sucesso!")
    st.switch_page("PaginasStreamlit/st_login.py")