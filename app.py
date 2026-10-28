import json
import gspread
import pandas as pd
import streamlit as st

# ======================= CONFIGURAÇÕES =======================
PLANILHA_ID = "1AhC0DeQFA1tQyrT3ldvDun_jy2DC-Dur3WF_yOBf4qQ"
NOME_ABA_USUARIOS = "usuarios"

st.set_page_config(
    page_title="Sistema de Acesso - Streamlit",
    page_icon="🔒",
    layout="wide"
)

# ======================= CONEXÃO COM O GOOGLE SHEETS =======================
@st.cache_resource
def conectar_google_sheets():
    """Autentica no Google Sheets usando as credenciais do st.secrets ou arquivo local."""
    try:
        # Tenta conectar via st.secrets (padrão de nuvem/Streamlit Cloud)
        if "gspread_credentials" in st.secrets:
            info_json = st.secrets["gspread_credentials"]["json_string"]
            dic_chaves = json.loads(info_json, strict=False)
            if "private_key" in dic_chaves:
                dic_chaves["private_key"] = dic_chaves["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
            client = gspread.service_account_from_dict(dic_chaves)
        else:
            # Fallback para o arquivo credentials.json local
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            client = gspread.service_account(filename="credentials.json", scopes=scope)
            
        return client.open_by_key(PLANILHA_ID)
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {e}")
        return None

@st.cache_data(ttl=30)
def buscar_usuarios():
    """Lê os usuários e permissões cadastrados na aba 'usuarios'."""
    sh = conectar_google_sheets()
    if not sh:
        return {}
    
    try:
        sheet = sh.worksheet(NOME_ABA_USUARIOS)
        registros = sheet.get_all_records()
        usuarios_dict = {}
        
        for reg in registros:
            usr = str(reg.get("usuario", "")).strip().lower()
            if usr:
                usuarios_dict[usr] = {
                    "senha": str(reg.get("senha", "")).strip(),
                    "nome": str(reg.get("nome", "")).strip(),
                    "ativo": str(reg.get("ativo", "NAO")).strip().upper(),
                    "consulta": str(reg.get("consulta", "NAO")).strip().upper(),
                    "casos": str(reg.get("casos", "NAO")).strip().upper()
                }
        return usuarios_dict
    except Exception as e:
        st.error(f"Erro ao ler a aba '{NOME_ABA_USUARIOS}': {e}")
        return {}

# ======================= CONTROLE DE SESSÃO =======================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.permissoes = {}
    st.session_state.pagina_atual = None

def realizar_login(usuario_input, senha_input):
    usuarios = buscar_usuarios()
    usr_key = usuario_input.strip().lower()

    if not usuarios:
        st.error("Nenhum usuário cadastrado ou erro na leitura da planilha.")
        return

    if usr_key in usuarios:
        dados = usuarios[usr_key]
        if dados["ativo"] != "SIM":
            st.error("Usuário inativo. Solicite acesso ao administrador.")
        elif dados["senha"] == senha_input.strip():
            st.session_state.autenticado = True
            st.session_state.usuario = usr_key
            st.session_state.nome = dados["nome"]
            st.session_state.permissoes = {
                "consulta": dados["consulta"],
                "casos": dados["casos"]
            }
            
            # Define a primeira aba permitida como padrão
            if dados["consulta"] == "SIM":
                st.session_state.pagina_atual = "consulta"
            elif dados["casos"] == "SIM":
                st.session_state.pagina_atual = "casos"
            else:
                st.session_state.pagina_atual = "sem_permissao"
                
            st.rerun()
        else:
            st.error("Senha incorreta.")
    else:
        st.error("Usuário não encontrado.")

def realizar_logout():
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.permissoes = {}
    st.session_state.pagina_atual = None
    st.rerun()


# ======================= TELA DE LOGIN =======================
if not st.session_state.autenticado:
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #f0f3ff 0%, #e3e9fd 100%); }
            [data-testid="stTextInput"] input { text-align: center !important; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.title("🔒 Autenticação de Usuário")
            st.caption("Acesso Restrito ao Painel de Controle")
            st.divider()

            usuario_input = st.text_input("Usuário")
            senha_input = st.text_input("Senha", type="password")

            btn_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if btn_entrar:
            if not usuario_input or not senha_input:
                st.warning("Preencha usuário e senha.")
            else:
                realizar_login(usuario_input, senha_input)

    st.stop()


# ======================= PAINEL PRINCIPAL LOGADO =======================

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.nome}")
    st.caption(f"Usuário: `{st.session_state.usuario}`")
    st.divider()

    st.markdown("**Navegação:**")
    
    # Exibe apenas os botões das abas com permissão SIM
    if st.session_state.permissoes.get("consulta") == "SIM":
        if st.button("🔎 Consulta de Equipamentos", use_container_width=True,
                     type="primary" if st.session_state.pagina_atual == "consulta" else "secondary"):
            st.session_state.pagina_atual = "consulta"
            st.rerun()

    if st.session_state.permissoes.get("casos") == "SIM":
        if st.button("📋 Casos em Andamento", use_container_width=True,
                     type="primary" if st.session_state.pagina_atual == "casos" else "secondary"):
            st.session_state.pagina_atual = "casos"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Sair / Logout", type="secondary", use_container_width=True):
        realizar_logout()


# --- CONTEÚDO DAS PÁGINAS ---
st.title("🛠️ Sistema de Gestão e Acompanhamento")

if st.session_state.pagina_atual == "consulta":
    if st.session_state.permissoes.get("consulta") != "SIM":
        st.error("⛔ Você não tem permissão para acessar esta aba.")
        st.stop()
        
    st.subheader("🔎 Área de Consulta de Equipamentos")
    st.info("Aqui você pode inserir o campo de busca de Nota Fiscal, CAS-SO-BR ou Cliente.")

elif st.session_state.pagina_atual == "casos":
    if st.session_state.permissoes.get("casos") != "SIM":
        st.error("⛔ Você não tem permissão para acessar esta aba.")
        st.stop()

    st.subheader("📋 Área de Casos em Andamento")
    st.info("Aqui serão exibidos os indicadores (KPIs) e a tabela de acompanhamento de prazos.")

elif st.session_state.pagina_atual == "sem_permissao":
    st.warning("⚠️ Seu usuário está ativo, mas não possui permissão para acessar nenhuma aba específica. Contate o administrador.")
