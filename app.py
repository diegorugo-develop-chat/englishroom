import json
import html
import gspread
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# ======================= CONFIGURAÇÕES =======================
PLANILHA_ID = "1AhC0DeQFA1tQyrT3ldvDun_jy2DC-Dur3WF_yOBf4qQ"
NOME_ABA_USUARIOS = "usuarios"
NOME_ABA_PROGRESSO = "progresso"
NOME_ABA_VERBOS = "verbos_irregulares"

# ======================= PALETA =======================
COR_MARCA = "#C8A27C"
COR_MARCA_ESCURA = "#8B6F4E"
COR_AMARELO = "#FAD54B"
COR_ROSA = "#FADADD"
COR_VERDE = "#2D5A27"
COR_CEU = "#87CEEB"
COR_FUNDO = "#FDFBF7"
COR_TEXTO = "#2B2622"
COR_TEXTO_SUAVE = "#6B5F55"
COR_BORDA = "#EDE4D8"

st.set_page_config(
    page_title="CarolEnglish — Aulas de inglês",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================= ESTILOS GLOBAIS =======================
def inject_theme():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Nunito', sans-serif;
            color: {COR_TEXTO};
        }}

        h1, h2, h3 {{
            font-family: 'Fraunces', serif;
            letter-spacing: -0.01em;
        }}

        /* Esconde apenas o menu ⋮, o botão Deploy, o rodapé e a decoração */
        #MainMenu, footer {{ visibility: hidden; }}
        [data-testid="stMainMenu"],
        [data-testid="stAppDeployButton"],
        [data-testid="stStatusWidget"],
        [data-testid="stDecoration"] {{ display: none !important; }}

        [data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
        }}

        /* ---- Barra lateral SEMPRE aberta ---- */
        section[data-testid="stSidebar"] {{
            display: block !important;
            visibility: visible !important;
            transform: none !important;
            min-width: 280px !important;
            width: 280px !important;
            background: #FFFFFF;
            border-right: 1px solid {COR_BORDA};
        }}
        section[data-testid="stSidebar"][aria-expanded="false"] {{
            display: block !important;
            transform: none !important;
            margin-left: 0 !important;
        }}
        /* Esconde o botão de recolher e o de reabrir a barra */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}

        .stApp {{ background-color: {COR_FUNDO}; }}

        section[data-testid="stSidebar"] > div:first-child {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding-bottom: 1rem;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            width: 100%;
            justify-content: flex-start;
            border: none;
            border-radius: 12px;
            padding: 0.7rem 1rem;
            background: transparent;
            color: {COR_TEXTO_SUAVE};
            font-weight: 700;
            font-size: 14px;
            text-align: left;
            transition: all 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background: {COR_ROSA};
            color: {COR_MARCA_ESCURA};
        }}
        section[data-testid="stSidebar"] .stButton button[kind="primary"] {{
            background: {COR_MARCA};
            color: #FFFFFF;
            box-shadow: 0 2px 8px rgba(200, 162, 124, 0.30);
        }}

        .stButton > button {{
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            transition: all 0.15s ease;
        }}

        .welcome-banner {{
            background: linear-gradient(120deg, {COR_MARCA} 0%, #D9B894 100%);
            border-radius: 20px;
            padding: 30px 34px;
            color: #FFFFFF;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }}
        .welcome-banner::after {{
            content: "✦";
            position: absolute;
            right: 28px;
            top: 18px;
            font-size: 2.2rem;
            color: {COR_AMARELO};
            opacity: 0.85;
        }}
        .welcome-banner h2 {{
            margin: 0 0 6px 0;
            font-size: 1.7rem;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .welcome-banner p {{
            margin: 0;
            opacity: 0.92;
            font-size: 0.95rem;
        }}

        .metric-card {{
            background: #FFFFFF;
            border-radius: 16px;
            padding: 20px 16px;
            border: 1px solid {COR_BORDA};
            text-align: center;
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .metric-card h3 {{
            margin: 0 0 4px 0;
            font-size: 2rem;
            font-weight: 800;
            color: {COR_MARCA_ESCURA};
            font-family: 'Fraunces', serif;
        }}
        .metric-card p {{
            margin: 0;
            color: {COR_TEXTO_SUAVE};
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}

        .topic-header-tag {{
            color: {COR_MARCA_ESCURA};
            font-weight: 800;
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .topic-title {{
            font-family: 'Fraunces', serif;
            font-size: 36px;
            font-weight: 800;
            color: {COR_TEXTO};
            margin: 0 0 8px 0;
            line-height: 1.2;
        }}
        .topic-subtitle {{
            color: {COR_TEXTO_SUAVE};
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .section-tag {{
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            color: {COR_MARCA_ESCURA};
            text-transform: uppercase;
            margin-top: 24px;
            margin-bottom: 12px;
        }}
        .info-box-light {{
            background: #FFFFFF;
            border: 1px solid {COR_BORDA};
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            color: {COR_TEXTO};
            font-size: 15px;
            line-height: 1.7;
        }}
        .struct-row {{
            background: #FBF7F1;
            border-radius: 10px;
            padding: 12px 18px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            font-family: ui-monospace, monospace;
            font-size: 14px;
        }}
        .struct-symbol {{
            font-weight: bold;
            width: 30px;
            color: {COR_MARCA_ESCURA};
        }}
        .tip-card-green {{
            background: #F3F8F1;
            border: 1px solid #CFE3C8;
            border-radius: 14px;
            padding: 16px;
            color: {COR_VERDE};
            font-size: 14px;
            line-height: 1.65;
        }}
        .error-card {{
            background: #FFFFFF;
            border: 1px solid {COR_BORDA};
            border-radius: 14px;
            padding: 16px;
            font-size: 14px;
        }}
        .err-wrong {{
            color: #B4453C;
            text-decoration: line-through;
            font-weight: 700;
        }}
        .err-correct {{
            color: {COR_VERDE};
            font-weight: 800;
        }}

        .ex-card-correct {{
            background-color: #F3F8F1;
            border: 1px solid #CFE3C8;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            font-size: 15px;
        }}
        .ex-card-wrong {{
            background-color: #FDF3F2;
            border: 1px solid #F2D5D2;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            font-size: 15px;
        }}
        .ex-card-neutral {{
            background-color: #FFFFFF;
            border: 1px solid {COR_BORDA};
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            font-size: 15px;
        }}

        .login-hero h1 {{
            font-family: 'Fraunces', serif;
            color: {COR_MARCA_ESCURA};
            font-size: 2.5rem;
            line-height: 1.2;
            font-weight: 800;
            margin: 0 0 1rem 0;
        }}
        .login-hero p {{
            font-size: 1.05rem;
            color: {COR_TEXTO_SUAVE};
            line-height: 1.7;
            margin: 0 0 1.5rem 0;
        }}
        .login-hero .destaque {{
            font-size: 0.95rem;
            color: {COR_TEXTO_SUAVE};
        }}
        .login-badge {{
            display: inline-block;
            background: {COR_ROSA};
            color: {COR_MARCA_ESCURA};
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 20px;
            margin-bottom: 1.2rem;
        }}
        .login-footer {{
            text-align: center;
            font-size: 0.85rem;
            color: {COR_TEXTO_SUAVE};
            margin-top: 1rem;
        }}
        .login-footer a {{
            color: {COR_MARCA_ESCURA};
            font-weight: 800;
            text-decoration: none;
        }}
        .divider-ou {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.2rem 0;
            color: {COR_TEXTO_SUAVE};
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .divider-ou::before, .divider-ou::after {{
            content: "";
            flex: 1;
            height: 1px;
            background: {COR_BORDA};
        }}
    </style>
    """, unsafe_allow_html=True)

inject_theme()

# ======================= CONEXÃO COM O GOOGLE SHEETS =======================
# Só o cliente fica em cache. Se a conexão falhar, a próxima tentativa refaz a conexão.
@st.cache_resource(show_spinner=False)
def _cliente_gspread():
    if "gspread_credentials" in st.secrets:
        info_json = st.secrets["gspread_credentials"]["json_string"]
        dic_chaves = json.loads(info_json, strict=False)
        if "private_key" in dic_chaves:
            dic_chaves["private_key"] = dic_chaves["private_key"].replace("\\\\n", "\n").replace("\\n", "\n")
        return gspread.service_account_from_dict(dic_chaves)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.service_account(filename="credentials.json", scopes=scope)

def conectar_google_sheets():
    try:
        return _cliente_gspread().open_by_key(PLANILHA_ID)
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {e}")
        return None

@st.cache_data(ttl=30)
def buscar_usuarios():
    sh = conectar_google_sheets()
    if sh is None:
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
                    "ativo": str(reg.get("ativo", "SIM")).strip().upper(),
                    "email": str(reg.get("email", "")).strip().lower(),
                    "niveis": {
                        "A1": str(reg.get("A1", "NAO")).strip().upper(),
                        "A2": str(reg.get("A2", "NAO")).strip().upper(),
                        "B1": str(reg.get("B1", "NAO")).strip().upper(),
                        "B2": str(reg.get("B2", "NAO")).strip().upper(),
                        "C1": str(reg.get("C1", "NAO")).strip().upper(),
                        "C2": str(reg.get("C2", "NAO")).strip().upper(),
                    }
                }
        return usuarios_dict
    except Exception as e:
        st.error(f"Erro ao ler a aba de utilizadores: {e}")
        return {}

@st.cache_data(ttl=60)
def carregar_verbos_irregulares():
    sh = conectar_google_sheets()
    if sh is None:
        return []
    try:
        return sh.worksheet(NOME_ABA_VERBOS).get_all_records()
    except Exception as e:
        st.error(f"Erro ao carregar verbos da planilha: {e}")
        return []

def carregar_progresso_usuario(usuario):
    sh = conectar_google_sheets()
    if sh is None:
        return {"xp": 0, "streak": 0, "gems": 0, "licoes_concluidas": 0}
    try:
        sheet = sh.worksheet(NOME_ABA_PROGRESSO)
        registros = sheet.get_all_records()
        for idx, reg in enumerate(registros, start=2):
            if str(reg.get("usuario", "")).strip().lower() == usuario.lower():
                return {
                    "linha": idx,
                    "xp": int(reg.get("xp") or 0),
                    "streak": int(reg.get("streak") or 0),
                    "gems": int(reg.get("gems") or 0),
                    "licoes_concluidas": int(reg.get("licoes_concluidas") or 0)
                }
        hoje = datetime.now().strftime("%d/%m/%Y")
        nova_linha = [usuario.lower(), 100, 1, 50, 1, hoje]
        sheet.append_row(nova_linha)
        return {"linha": len(registros) + 2, "xp": 100, "streak": 1, "gems": 50, "licoes_concluidas": 1}
    except Exception as e:
        st.warning(f"Não foi possível carregar seu progresso: {e}")
        return {"xp": 0, "streak": 0, "gems": 0, "licoes_concluidas": 0}

def atualizar_progresso_no_sheets(usuario, xp_add=0, gems_add=0, licoes_add=0):
    sh = conectar_google_sheets()
    if sh is None:
        return
    try:
        sheet = sh.worksheet(NOME_ABA_PROGRESSO)
        prog = carregar_progresso_usuario(usuario)
        linha = prog.get("linha")

        novo_xp = prog["xp"] + xp_add
        novas_gems = prog["gems"] + gems_add
        novas_licoes = prog["licoes_concluidas"] + licoes_add
        hoje = datetime.now().strftime("%d/%m/%Y")

        sheet.update_cell(linha, 2, novo_xp)
        sheet.update_cell(linha, 4, novas_gems)
        sheet.update_cell(linha, 5, novas_licoes)
        sheet.update_cell(linha, 6, hoje)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Erro ao salvar progresso: {e}")

# ======================= CONTROLE DE SESSÃO =======================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.niveis = {}
    st.session_state.pagina_atual = "dashboard"
    st.session_state.topico_selecionado = None

def trocar_pagina(pagina):
    st.session_state.pagina_atual = pagina
    st.session_state.topico_selecionado = None
    st.rerun()

def autenticar_por_email(email):
    """Busca o aluno pelo e-mail Google na planilha."""
    usuarios = buscar_usuarios()
    email_key = email.strip().lower()

    for chave, dados in usuarios.items():
        if dados.get("email") == email_key or chave == email_key:
            if dados["ativo"] != "SIM":
                return None, "inativo"
            return dados, "ok"

    return None, "nao_encontrado"

def iniciar_sessao(dados, identificador):
    st.session_state.autenticado = True
    st.session_state.usuario = identificador
    st.session_state.nome = dados["nome"]
    st.session_state.niveis = dados["niveis"]
    st.session_state.pagina_atual = "dashboard"

def realizar_login_senha(usuario_input, senha_input):
    usuarios = buscar_usuarios()
    usr_key = usuario_input.strip().lower()

    if usr_key in usuarios:
        dados = usuarios[usr_key]
        if dados["ativo"] != "SIM":
            st.error("Conta inativa. Fale com a professora para liberar o acesso.")
        elif dados["senha"] == senha_input.strip():
            iniciar_sessao(dados, usr_key)
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")
    else:
        st.error("Usuário não encontrado. Confira ou fale com a professora.")

def realizar_logout():
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.niveis = {}
    try:
        if st.user.is_logged_in:
            st.logout()
    except Exception:
        pass
    st.rerun()

# ======================= TELA DE LOGIN =======================
if not st.session_state.autenticado:

    google_configurado = False
    try:
        google_configurado = "auth" in st.secrets
    except Exception:
        google_configurado = False

    if google_configurado:
        try:
            if st.user.is_logged_in:
                dados_aluno, status = autenticar_por_email(st.user.email)

                if status == "ok":
                    iniciar_sessao(dados_aluno, st.user.email.lower())
                    st.rerun()
                elif status == "inativo":
                    st.error(f"A conta **{st.user.email}** está inativa.")
                    st.caption("Fale com a professora para liberar o acesso.")
                    if st.button("Sair da conta Google"):
                        st.logout()
                    st.stop()
                else:
                    st.error(f"A conta **{st.user.email}** não está cadastrada.")
                    st.caption("Fale com a professora para solicitar seu acesso.")
                    if st.button("Sair da conta Google"):
                        st.logout()
                    st.stop()
        except Exception:
            pass

    st.markdown(f"<style>.stApp {{ background: {COR_FUNDO}; }}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 6vh'></div>", unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1.15, 1], gap="large")

    with col_esq:
        st.markdown("""
            <div class="login-hero">
                <div class="login-badge">English Teacher · Aulas 1:1</div>
                <h1>I've tried everything.<br>Nothing made me as happy<br>as teaching English.</h1>
                <p>
                    Aulas particulares com trilha personalizada,
                    prática de conversação e acompanhamento de progresso.
                </p>
                <p class="destaque">
                    Já é aluna(o)? Entre ao lado para continuar sua trilha.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col_dir:
        st.markdown("<div style='height: 6vh'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<h3 style='margin-bottom:0.2rem; font-family:Fraunces,serif; color:{COR_TEXTO};'>Entrar na sua conta</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{COR_TEXTO_SUAVE}; font-size:0.9rem; margin-bottom:1rem;'>Use a conta Google cadastrada pela professora.</p>", unsafe_allow_html=True)

            if google_configurado:
                if st.button("Continuar com Google", type="primary", use_container_width=True):
                    st.login("google")

                st.markdown('<div class="divider-ou">ou</div>', unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                usuario_input = st.text_input("Usuário", placeholder="seu usuário", autocomplete="off")
                senha_input = st.text_input("Senha", type="password", placeholder="Sua senha", autocomplete="off")
                btn_entrar = st.form_submit_button("Entrar com senha", use_container_width=True)

            st.markdown("""
                <p class="login-footer">
                    Ainda não tem conta?
                    <a href="https://instagram.com/teacher.carolinealencar">Fale com a teacher</a>
                </p>
            """, unsafe_allow_html=True)

        if btn_entrar:
            if not usuario_input or not senha_input:
                st.warning("Preencha o usuário e a senha.")
            else:
                realizar_login_senha(usuario_input, senha_input)

    st.stop()


# ======================= SISTEMA PRINCIPAL =======================
dados_progresso = carregar_progresso_usuario(st.session_state.usuario)

# --- MENU LATERAL (sempre visível) ---
with st.sidebar:
    st.markdown(f"""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size:1.15rem; font-weight:800; color:{COR_MARCA_ESCURA}; font-family:Fraunces,serif;">
                CarolEnglish
            </div>
            <div style="font-size:0.72rem; color:{COR_TEXTO_SUAVE}; letter-spacing:1px; text-transform:uppercase; font-weight:700; margin-top:2px;">
                English Teacher
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background:{COR_ROSA}; border-radius:12px; padding:12px 14px; margin-bottom:16px;">
            <div style="font-size:0.75rem; color:{COR_MARCA_ESCURA}; margin-bottom:2px; font-weight:700;">Aluna(o)</div>
            <div style="font-weight:800; color:{COR_TEXTO}; font-size:0.95rem;">{st.session_state.nome}</div>
        </div>
    """, unsafe_allow_html=True)

    niveis_ativos = [nv for nv, status in st.session_state.niveis.items() if status == "SIM"]
    st.caption(f"Níveis liberados: **{', '.join(niveis_ativos) if niveis_ativos else 'Nenhum'}**")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    pagina_ativa = st.session_state.pagina_atual

    if st.button("📊  Dashboard", key="side_dashboard", use_container_width=True,
                 type="primary" if pagina_ativa == "dashboard" else "secondary"):
        trocar_pagina("dashboard")

    if st.button("🚀  Trilha de aprendizado", key="side_skills", use_container_width=True,
                 type="primary" if pagina_ativa == "skills" else "secondary"):
        trocar_pagina("skills")

    if st.button("🔄  Verbos irregulares", key="side_verbs", use_container_width=True,
                 type="primary" if pagina_ativa == "verbs" else "secondary"):
        trocar_pagina("verbs")

    if st.button("💬  Prática com IA", key="side_practice", use_container_width=True,
                 type="primary" if pagina_ativa == "practice" else "secondary"):
        trocar_pagina("practice")

    st.markdown(f'<div style="margin-top:auto; padding-top:1rem; border-top:1px solid {COR_BORDA};"></div>', unsafe_allow_html=True)
    if st.button("Sair", key="side_sair", use_container_width=True, type="secondary"):
        realizar_logout()

    st.markdown(f"""
        <div style="text-align:center; font-size:0.7rem; color:{COR_TEXTO_SUAVE}; padding-top:8px; letter-spacing:1px; font-weight:700;">
            XOXO
        </div>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO NO TOPO (reserva, caso a lateral não apareça) ---
opcoes_nav = [
    ("dashboard", "📊 Dashboard"),
    ("skills", "🚀 Trilha"),
    ("verbs", "🔄 Verbos"),
    ("practice", "💬 Prática IA"),
]
cols_nav = st.columns(len(opcoes_nav))
for col, (chave, rotulo) in zip(cols_nav, opcoes_nav):
    with col:
        if st.button(rotulo, key=f"top_{chave}", use_container_width=True,
                     type="primary" if st.session_state.pagina_atual == chave else "secondary"):
            trocar_pagina(chave)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ======================= FUNÇÕES AUXILIARES DE VERBOS =======================
def pegar_campo(registro, *nomes):
    """Retorna o primeiro campo preenchido, ignorando maiúsculas e espaços nos nomes das colunas."""
    mapa = {str(k).strip().lower(): v for k, v in registro.items()}
    for nome in nomes:
        valor = mapa.get(nome.lower())
        if valor not in (None, ""):
            return str(valor).strip()
    return ""

def card_verbo(base, passado, participio, traducao):
    """Card com botão de pronúncia. Usa components.html porque st.markdown remove <script>."""
    html_card = """
    <div style="font-family:Nunito,sans-serif; background:#FFFFFF; border:1px solid #EDE4D8;
                border-radius:16px; padding:16px; text-align:center; box-sizing:border-box;">
      <div style="font-family:Fraunces,serif; font-size:24px; font-weight:800; color:#2B2622;">__BASE__</div>
      <div style="color:#6B5F55; font-size:14px; margin:6px 0;">__PASSADO__ · __PARTICIPIO__</div>
      <div style="color:#8B6F4E; font-size:13px; margin-bottom:10px;">__TRADUCAO__</div>
      <button id="btn" style="background:#C8A27C; color:#FFFFFF; border:none; border-radius:12px;
              padding:8px 14px; font-weight:700; cursor:pointer; font-family:Nunito,sans-serif;">🔊 Ouvir</button>
    </div>
    <script>
      const texto = __TEXTO_JS__;
      document.getElementById("btn").onclick = () => {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(texto);
        u.lang = "en-US";
        u.rate = 0.9;
        window.speechSynthesis.speak(u);
      };
    </script>
    """
    html_card = (html_card
                 .replace("__BASE__", html.escape(base))
                 .replace("__PASSADO__", html.escape(passado or "—"))
                 .replace("__PARTICIPIO__", html.escape(participio or "—"))
                 .replace("__TRADUCAO__", html.escape(traducao))
                 .replace("__TEXTO_JS__", json.dumps(base)))
    components.html(html_card, height=190)


# ======================= CORTE DE PÁGINAS =======================
pagina = st.session_state.pagina_atual

if pagina == "dashboard":
    st.markdown(f"""
        <div class="welcome-banner">
            <h2>Olá, {st.session_state.nome}!</h2>
            <p>Continue mantendo sua sequência de estudos em dia.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["xp"]}</h3><p>XP acumulado</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["streak"]}</h3><p>Dias seguidos</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["gems"]}</h3><p>Gems</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["licoes_concluidas"]}</h3><p>Lições concluídas</p></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.subheader("Ações rápidas")
    if st.button("Concluir lição de exemplo (+50 XP e +10 Gems)"):
        atualizar_progresso_no_sheets(st.session_state.usuario, xp_add=50, gems_add=10, licoes_add=1)
        st.success("Atividade registrada. Seu progresso foi salvo.")
        st.rerun()

elif pagina == "skills":
    # [COLE AQUI o dicionário trilha_dados completo do seu arquivo original.]
    trilha_dados = {}

    if st.session_state.get("topico_selecionado"):
        topico = st.session_state.topico_selecionado
        col_voltar, col_vazia = st.columns([1, 4])
        with col_voltar:
            if st.button("⬅️  Voltar à trilha"):
                st.session_state.topico_selecionado = None
                st.rerun()
        st.markdown('<div class="topic-header-tag">A1 · Iniciante</div>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="topic-title">{topico}</h1>', unsafe_allow_html=True)
        st.markdown('<div class="topic-subtitle">O verbo que significa <b>ser</b> e <b>estar</b> ao mesmo tempo.</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px;">
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">A ideia</span>
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">Estrutura</span>
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">Exemplos</span>
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">Dicas</span>
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">Erros comuns</span>
                <span style="background:{COR_ROSA}; padding: 6px 14px; border-radius: 20px; font-size:13px; font-weight:700; color:{COR_MARCA_ESCURA};">Pratique</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-tag">A IDEIA</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="info-box-light">
                Usamos o <b>to be</b> para dizer quem somos, de onde somos, nossa idade, profissão, como estamos e onde estamos.
                Em português temos dois verbos (ser e estar); em inglês, um só faz os dois papéis. Ele muda conforme a pessoa:
                <b style="color:{COR_MARCA_ESCURA};">am</b> com I, <b style="color:{COR_MARCA_ESCURA};">is</b> com he/she/it e <b style="color:{COR_MARCA_ESCURA};">are</b> com you/we/they.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-tag">ESTRUTURA</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="info-box-light">
                <div class="struct-row"><span class="struct-symbol">+</span><span>I <b>am</b> (I'm) &nbsp;·&nbsp; he/she/it <b>is</b> (she's) &nbsp;·&nbsp; you/we/they <b>are</b> (we're)</span></div>
                <div class="struct-row"><span class="struct-symbol">-</span><span>I'm <b>not</b> &nbsp;·&nbsp; she <b>isn't</b> &nbsp;·&nbsp; they <b>aren't</b></span></div>
                <div class="struct-row"><span class="struct-symbol">?</span><span><b>Am</b> I...? &nbsp;·&nbsp; <b>Is</b> he...? &nbsp;·&nbsp; <b>Are</b> you...?</span></div>
                <div class="struct-row"><span class="struct-symbol">✓</span><span>Respostas curtas: Yes, I <b>am</b>. / No, she <b>isn't</b>.</span></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-tag">EXEMPLOS</div>', unsafe_allow_html=True)
        st.caption("Toque na frase para ver a tradução")
        ex1, ex2 = st.columns(2)
        with ex1:
            st.info("I **am** 14 years old.  \n*(Eu tenho 14 anos de idade.)*")
            st.info("We **aren't** tired. We're excited!  \n*(Nós não estamos cansados. Estamos empolgados!)*")
        with ex2:
            st.info("My best friend **is** from Curitiba.  \n*(O meu melhor amigo é de Curitiba.)*")
            st.info("**Is** your mom a teacher? – Yes, she **is**.  \n*(A tua mãe é professora? – Sim, é.)*")
        col_dicas, col_erros = st.columns(2)
        with col_dicas:
            st.markdown('<div class="section-tag">DICAS</div>', unsafe_allow_html=True)
            st.markdown("""
                <div class="tip-card-green">
                    <b>Idade é com BE</b><br>Em inglês, você <i>é</i> a sua idade: <i>I'm 15</i>. Nunca <i>I have 15</i>.
                    <br><br><b>Sentimentos também</b><br>Fome, sede, frio e medo usam <i>be</i>: <i>I'm hungry, I'm cold</i>.
                </div>
            """, unsafe_allow_html=True)
        with col_erros:
            st.markdown('<div class="section-tag">ERROS COMUNS</div>', unsafe_allow_html=True)
            st.markdown("""
                <div class="error-card">
                    <span class="err-wrong">I have 13 years.</span><br><span class="err-correct">I am 13 years old.</span><br><small style="color:#6B5F55;">Idade usa be, não have.</small>
                    <hr style="margin: 8px 0; border-top:1px solid #F1EAE0;">
                    <span class="err-wrong">She are my sister.</span><br><span class="err-correct">She is my sister.</span><br><small style="color:#6B5F55;">Com he/she/it, use sempre is.</small>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('<div class="section-tag">PRATIQUE</div>', unsafe_allow_html=True)
        st.markdown("### Exercícios interativos")
        st.caption("Clique nas opções abaixo ou preencha os campos para conferir.")
        if "respostas_submetidas" not in st.session_state:
            st.session_state.respostas_submetidas = {}
        acertos_atuais = sum(1 for k, v in st.session_state.respostas_submetidas.items() if v == "correto")
        st.markdown(f"**{acertos_atuais} / 5 acertos**")
        st.progress(acertos_atuais / 5)
        st.markdown("<br>", unsafe_allow_html=True)
        status_q1 = st.session_state.respostas_submetidas.get("q1", None)
        if status_q1 == "correto":
            st.markdown('<div class="ex-card-correct">1. My friends ___ very funny.<br><br>✅ <b>Isso!</b> A resposta é <b>are</b>. <i>My friends</i> = they → are.</div>', unsafe_allow_html=True)
        elif status_q1 == "errado":
            st.markdown('<div class="ex-card-wrong">1. My friends ___ very funny.<br><br>❌ <b>Quase.</b> A resposta é <b>are</b>. <i>My friends</i> = they → are.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ex-card-neutral">1. My friends ___ very funny.</div>', unsafe_allow_html=True)
            bc1, bc2, bc3 = st.columns([1, 1, 1])
            with bc1:
                if st.button("is", key="btn_q1_is", use_container_width=True):
                    st.session_state.respostas_submetidas["q1"] = "errado"
                    st.rerun()
            with bc2:
                if st.button("am", key="btn_q1_am", use_container_width=True):
                    st.session_state.respostas_submetidas["q1"] = "errado"
                    st.rerun()
            with bc3:
                if st.button("are", key="btn_q1_are", use_container_width=True):
                    st.session_state.respostas_submetidas["q1"] = "correto"
                    atualizar_progresso_no_sheets(st.session_state.usuario, xp_add=10, gems_add=2)
                    st.rerun()
        status_q2 = st.session_state.respostas_submetidas.get("q2", None)
        if status_q2 == "correto":
            st.markdown('<div class="ex-card-correct">2. ___ you hungry?<br><br>✅ <b>Isso!</b> Pergunta com <i>you</i> → Are.</div>', unsafe_allow_html=True)
        elif status_q2 == "errado":
            st.markdown('<div class="ex-card-wrong">2. ___ you hungry?<br><br>❌ <b>Incorreto.</b> A resposta certa é <b>Are</b>.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ex-card-neutral">2. ___ you hungry?</div>', unsafe_allow_html=True)
        # [COLE AQUI o restante da aba Trilha, a partir da questão 3, do seu arquivo original.]

elif pagina == "verbs":
    st.markdown('<div class="topic-header-tag">Verbos irregulares</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="topic-title">Verbos irregulares</h1>', unsafe_allow_html=True)
    st.markdown('<div class="topic-subtitle">Clique em 🔊 em cada card para ouvir a pronúncia.</div>', unsafe_allow_html=True)

    verbos = carregar_verbos_irregulares()

    if not verbos:
        st.warning(
            "Nenhum verbo carregado. Confira se a aba 'verbos_irregulares' existe na planilha, "
            "se a primeira linha tem os cabeçalhos e se a conexão com o Google Sheets está ativa."
        )
    else:
        colunas = st.columns(3, gap="medium")
        exibidos = 0
        for registro in verbos:
            base = pegar_campo(registro, "verbo", "infinitivo", "base", "infinitive")
            if not base:
                continue
            passado = pegar_campo(registro, "passado", "past", "simple past")
            participio = pegar_campo(registro, "particípio", "participio", "past participle", "pp")
            traducao = pegar_campo(registro, "tradução", "traducao", "significado", "translation")
            with colunas[exibidos % 3]:
                card_verbo(base, passado, participio, traducao)
            exibidos += 1

        if exibidos == 0:
            st.warning("A planilha foi lida, mas nenhuma linha tem a coluna 'verbo' preenchida. Confira os cabeçalhos.")

elif pagina == "practice":
    # [COLE AQUI o bloco da Prática com IA do seu arquivo original.]
    st.info("Esta aba está em construção.")
