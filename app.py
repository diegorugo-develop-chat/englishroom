import json
import gspread
import pandas as pd
import streamlit as st

# ======================= CONFIGURAÇÕES =======================
PLANILHA_ID = "1AhC0DeQFA1tQyrT3ldvDun_jy2DC-Dur3WF_yOBf4qQ"
NOME_ABA_USUARIOS = "usuarios"

st.set_page_config(
    page_title="CarolEnglish — Plataforma de Ensino",
    page_icon="💜",
    layout="wide"
)

# ======================= ESTILOS CSS (ESTILO LEARNIQ / MODERN) =======================
st.markdown("""
    <style>
        /* Fundo geral suave */
        .stApp {
            background-color: #f4f6fc;
            font-family: 'Inter', sans-serif;
        }
        
        /* Estilização da Sidebar (Menu Lateral Roxo Elegante) */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #eaeaea;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            justify-content: flex-start;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            background: transparent;
            color: #5c6b73;
            font-weight: 600;
            font-size: 14px;
            text-align: left;
            transition: all 0.2s;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: #f0f3ff;
            color: #4f67e8;
        }
        section[data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: linear-gradient(110deg, #8aa0ff, #4f67e8);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(79, 103, 232, 0.25);
        }

        /* Cartões do Dashboard */
        .welcome-banner {
            background: linear-gradient(110deg, #8aa0ff, #4f67e8);
            border-radius: 20px;
            padding: 28px;
            color: white;
            box-shadow: 0 10px 25px rgba(79, 103, 232, 0.2);
            margin-bottom: 24px;
        }
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.04);
            text-align: center;
            border-top: 4px solid #4f67e8;
        }
        .content-card {
            background: white;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.04);
            margin-bottom: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ======================= CONEXÃO COM O GOOGLE SHEETS =======================
@st.cache_resource
def conectar_google_sheets():
    try:
        if "gspread_credentials" in st.secrets:
            info_json = st.secrets["gspread_credentials"]["json_string"]
            dic_chaves = json.loads(info_json, strict=False)
            if "private_key" in dic_chaves:
                dic_chaves["private_key"] = dic_chaves["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
            client = gspread.service_account_from_dict(dic_chaves)
        else:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            client = gspread.service_account(filename="credentials.json", scopes=scope)
        return client.open_by_key(PLANILHA_ID)
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {e}")
        return None

@st.cache_data(ttl=30)
def buscar_usuarios():
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
        st.error(f"Erro ao ler a aba de usuários: {e}")
        return {}

# ======================= CONTROLE DE SESSÃO =======================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.permissoes = {}
    st.session_state.pagina_atual = "dashboard"

def realizar_login(usuario_input, senha_input):
    usuarios = buscar_usuarios()
    usr_key = usuario_input.strip().lower()

    if usr_key in usuarios:
        dados = usuarios[usr_key]
        if dados["ativo"] != "SIM":
            st.error("Usuário inativo. Solicite liberação.")
        elif dados["senha"] == senha_input.strip():
            st.session_state.autenticado = True
            st.session_state.usuario = usr_key
            st.session_state.nome = dados["nome"]
            st.session_state.permissoes = {
                "consulta": dados["consulta"],
                "casos": dados["casos"]
            }
            st.session_state.pagina_atual = "dashboard"
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
            st.title("💜 CarolEnglish")
            st.caption("Faça login para acessar sua plataforma")
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


# ======================= SISTEMA PRINCIPAL (PÓS-LOGIN) =======================

# --- MENU LATERAL (ESTILO LEARNIQ) ---
with st.sidebar:
    st.markdown("### 💜 CarolEnglish")
    st.caption(f"Aluno(a): **{st.session_state.nome}**")
    st.divider()

    # Botões do Menu inspirados na referência visual
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dashboard" else "secondary"):
        st.session_state.pagina_atual = "dashboard"
        st.rerun()

    if st.button("🚀 Skills / Trilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "skills" else "secondary"):
        st.session_state.pagina_atual = "skills"
        st.rerun()

    if st.button("💬 Practice & AI", use_container_width=True, type="primary" if st.session_state.pagina_atual == "practice" else "secondary"):
        st.session_state.pagina_atual = "practice"
        st.rerun()

    # Abas dinâmicas controladas pela planilha do Google Sheets
    if st.session_state.permissoes.get("consulta") == "SIM":
        if st.button("🔎 Consulta de Equipamentos", use_container_width=True, type="primary" if st.session_state.pagina_atual == "consulta" else "secondary"):
            st.session
