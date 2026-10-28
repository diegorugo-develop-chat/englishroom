import json
import gspread
import pandas as pd
import streamlit as st

# ======================= CONFIGURAÇÕES =======================
PLANILHA_ID = "1AhC0DeQFA1tQyrT3ldvDun_jy2DC-Dur3WF_yOBf4qQ"
NOME_ABA_USUARIOS = "usuarios"

st.set_page_config(
    page_title="Yorésilient — Dashboard",
    page_icon="💜",
    layout="wide"
)

# ======================= ESTILOS CSS PERSONALIZADOS =======================
st.markdown("""
    <style>
        /* Fundo geral da aplicação */
        .stApp {
            background-color: #f8f9fc;
        }
        
        /* Estilização da Sidebar (Menu Lateral Roxo/Bordô) */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #6b215a 0%, #4a153f 100%);
            color: white;
        }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            justify-content: flex-start;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            background: transparent;
            color: #f3e8f1;
            font-weight: 500;
            text-align: left;
            transition: background 0.2s;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }
        section[data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
            font-weight: 700;
        }

        /* Cartões e Containers do Dashboard */
        .welcome-banner {
            background: linear-gradient(135deg, #4a153f 0%, #7b2c6bf0 100%);
            border-radius: 20px;
            padding: 30px;
            color: white;
            box-shadow: 0 10px 25px rgba(74, 21, 63, 0.15);
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            text-align: center;
            border-top: 4px solid #6b215a;
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
            st.title("💜 Yorésilient")
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

# --- MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("## 💜 Yorésilient")
    st.caption(f"Logado como: **{st.session_state.nome}**")
    st.divider()

    # Botões de Navegação (Você pode ir adicionando novos botões aqui aos poucos)
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dashboard" else "secondary"):
        st.session_state.pagina_atual = "dashboard"
        st.rerun()

    # Exibe aba
