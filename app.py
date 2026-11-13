import json
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

# ======================= PALETA (extraída das referências) =======================
COR_MARCA = "#C8A27C"          # ocre terroso
COR_MARCA_ESCURA = "#8B6F4E"   # ocre profundo
COR_AMARELO = "#FAD54B"        # amarelo dourado
COR_ROSA = "#FADADD"           # rosa pastel
COR_VERDE = "#2D5A27"          # verde botânico
COR_CEU = "#87CEEB"            # azul céu
COR_FUNDO = "#FDFBF7"          # off-white quente
COR_TEXTO = "#2B2622"          # marrom quase preto
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

        /* Oculta a barra do Streamlit */
        #MainMenu, footer, header {{ visibility: hidden; }}
        [data-testid="stToolbar"] {{ display: none; }}
        [data-testid="stDecoration"] {{ display: none; }}
        [data-testid="stStatusWidget"] {{ display: none; }}

        .stApp {{ background-color: {COR_FUNDO}; }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: #FFFFFF;
            border-right: 1px solid {COR_BORDA};
        }}
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

        /* Botões gerais */
        .stButton > button {{
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            transition: all 0.15s ease;
        }}

        /* Banner de boas-vindas */
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

        /* Cards de métrica */
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

        /* Página de lição */
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

        /* Cards de exercício */
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

        /* Login */
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
    </style>
    """, unsafe_allow_html=True)

inject_theme()

# Script global para síntese de voz nativa do navegador
st.markdown("""
    <script>
    function falar(texto) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'en-US';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }
    }
    </script>
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
                    "ativo": str(reg.get("ativo", "SIM")).strip().upper(),
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
    if not sh:
        return []
    try:
        sheet = sh.worksheet(NOME_ABA_VERBOS)
        return sheet.get_all_records()
    except Exception as e:
        st.error(f"Erro ao carregar verbos da planilha: {e}")
        return []

def carregar_progresso_usuario(usuario):
    sh = conectar_google_sheets()
    if not sh:
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
        return {"xp": 0, "streak": 0, "gems": 0, "licoes_concluidas": 0}

def atualizar_progresso_no_sheets(usuario, xp_add=0, gems_add=0, licoes_add=0):
    sh = conectar_google_sheets()
    if not sh:
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

def realizar_login(usuario_input, senha_input):
    usuarios = buscar_usuarios()
    usr_key = usuario_input.strip().lower()

    if usr_key in usuarios:
        dados = usuarios[usr_key]
        if dados["ativo"] != "SIM":
            st.error("Conta inativa. Fale com a professora para liberar o acesso.")
        elif dados["senha"] == senha_input.strip():
            st.session_state.autenticado = True
            st.session_state.usuario = usr_key
            st.session_state.nome = dados["nome"]
            st.session_state.niveis = dados["niveis"]
            st.session_state.pagina_atual = "dashboard"
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")
    else:
        st.error("E-mail não encontrado. Confira ou fale com a professora.")

def realizar_logout():
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.nome = None
    st.session_state.niveis = {}
    st.rerun()

# ======================= TELA DE LOGIN =======================
if not st.session_state.autenticado:
    st.markdown(f"<style>.stApp {{ background: {COR_FUNDO}; }}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 6vh'></div>", unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1.15, 1], gap="large")

    with col_esq:
        st.markdown(f"""
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
            st.markdown(f"<p style='color:{COR_TEXTO_SUAVE}; font-size:0.9rem; margin-bottom:1rem;'>Use o acesso enviado pela professora.</p>", unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                usuario_input = st.text_input("E-mail ou usuário", placeholder="seu@email.com", autocomplete="off")
                senha_input = st.text_input("Senha", type="password", placeholder="Sua senha", autocomplete="off")
                btn_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            st.markdown(f"""
                <p class="login-footer">
                    Ainda não tem conta?
                    <a href="https://instagram.com/teacher.carolinealencar">Fale com a teacher</a>
                </p>
            """, unsafe_allow_html=True)

        if btn_entrar:
            if not usuario_input or not senha_input:
                st.warning("Preencha o e-mail e a senha.")
            else:
                realizar_login(usuario_input, senha_input)

    st.stop()


# ======================= SISTEMA PRINCIPAL =======================
dados_progresso = carregar_progresso_usuario(st.session_state.usuario)

# --- MENU LATERAL ---
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

    if st.button("📊  Dashboard", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dashboard" else "secondary"):
        st.session_state.pagina_atual = "dashboard"
        st.session_state.topico_selecionado = None
        st.rerun()

    if st.button("🚀  Trilha de aprendizado", use_container_width=True, type="primary" if st.session_state.pagina_atual == "skills" else "secondary"):
        st.session_state.pagina_atual = "skills"
        st.session_state.topico_selecionado = None
        st.rerun()

    if st.button("🔄  Verbos irregulares", use_container_width=True, type="primary" if st.session_state.pagina_atual == "verbs" else "secondary"):
        st.session_state.pagina_atual = "verbs"
        st.session_state.topico_selecionado = None
        st.rerun()

    if st.button("💬  Prática com IA", use_container_width=True, type="primary" if st.session_state.pagina_atual == "practice" else "secondary"):
        st.session_state.pagina_atual = "practice"
        st.session_state.topico_selecionado = None
        st.rerun()

    # Logout fixo no rodapé
    st.markdown(f'<div style="margin-top:auto; padding-top:1rem; border-top:1px solid {COR_BORDA};"></div>', unsafe_allow_html=True)
    if st.button("Sair", use_container_width=True, type="secondary"):
        realizar_logout()

    st.markdown(f"""
        <div style="text-align:center; font-size:0.7rem; color:{COR_TEXTO_SUAVE}; padding-top:8px; letter-spacing:1px; font-weight:700;">
            XOXO
        </div>
    """, unsafe_allow_html=True)


# --- CORTE DE PÁGINAS ---
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
    trilha_dados = {
        "A1": {
            "titulo": "A1 · Iniciante",
            "topicos": [
                {"nome": "Verb to be", "sub": "am / is / are", "status": "em_andamento"},
                {"nome": "Subject & object pronouns", "sub": "I / me, she / her...", "status": "nao_comecou"},
                {"nome": "Possessives", "sub": "my, your, 's", "status": "nao_comecou"},
                {"nome": "Present simple", "sub": "rotinas, gostos e fatos", "status": "nao_comecou"},
                {"nome": "Present continuous", "sub": "o que está acontecendo agora", "status": "completo"},
                {"nome": "There is / there are", "sub": "existe, há, tem", "status": "em_andamento"},
                {"nome": "Articles a / an / the", "sub": "um, uma, o, a", "status": "em_andamento"},
                {"nome": "Plural nouns", "sub": "cats, boxes, children", "status": "em_andamento"},
                {"nome": "Can / can't", "sub": "habilidade, permissão e pedidos", "status": "nao_comecou"},
                {"nome": "Imperatives & Let's", "sub": "ordens, instruções e sugestões", "status": "nao_comecou"},
                {"nome": "Prepositions of time", "sub": "in / on / at", "status": "nao_comecou"},
                {"nome": "Prepositions of place", "sub": "in, on, under, next to...", "status": "nao_comecou"},
                {"nome": "Adverbs of frequency", "sub": "always, usually, never...", "status": "nao_comecou"},
                {"nome": "This / that / these / those", "sub": "este, esse, aquele", "status": "nao_comecou"},
                {"nome": "Question words", "sub": "what, where, when, why...", "status": "nao_comecou"}
            ]
        },
        "A2": {
            "titulo": "A2 · Básico",
            "topicos": [
                {"nome": "Was / were", "sub": "o passado do verb to be", "status": "nao_comecou"},
                {"nome": "Past simple", "sub": "ações terminadas no passado", "status": "nao_comecou"},
                {"nome": "Past continuous", "sub": "o que estava acontecendo", "status": "nao_comecou"},
                {"nome": "Comparatives & superlatives", "sub": "bigger, the biggest", "status": "nao_comecou"},
                {"nome": "Countable & uncountable", "sub": "some, any, much, many", "status": "nao_comecou"},
                {"nome": "Be going to", "sub": "planos e previsões com evidência", "status": "nao_comecou"},
                {"nome": "Will", "sub": "previsões, decisões na hora e promessas", "status": "nao_comecou"},
                {"nome": "Present perfect (experiences)", "sub": "ever, never, already, yet, just", "status": "nao_comecou"},
                {"nome": "Must / have to", "sub": "obrigação e proibição", "status": "nao_comecou"},
                {"nome": "Should", "sub": "conselhos e opiniões", "status": "nao_comecou"},
                {"nome": "Like / love / want + verb", "sub": "-ing ou to?", "status": "nao_comecou"},
                {"nome": "Too / enough", "sub": "demais, suficiente", "status": "nao_comecou"},
                {"nome": "Adverbs of manner", "sub": "quickly, carefully, well", "status": "nao_comecou"}
            ]
        },
        "B1": {
            "titulo": "B1 · Intermediário",
            "topicos": [
                {"nome": "Present perfect vs past simple", "sub": "quando usar cada um", "status": "nao_comecou"},
                {"nome": "Present perfect continuous", "sub": "for & since, how long", "status": "nao_comecou"},
                {"nome": "Used to", "sub": "hábitos do passado", "status": "nao_comecou"},
                {"nome": "Past perfect", "sub": "o passado do passado", "status": "nao_comecou"},
                {"nome": "Future forms", "sub": "will, going to ou present continuous?", "status": "nao_comecou"},
                {"nome": "Zero & first conditional", "sub": "fatos e futuro possível", "status": "nao_comecou"},
                {"nome": "Second conditional", "sub": "situações imaginárias", "status": "nao_comecou"},
                {"nome": "Passive voice (present & past)", "sub": "is made, was built", "status": "nao_comecou"},
                {"nome": "Defining relative clauses", "sub": "who, which, that, where, whose", "status": "nao_comecou"},
                {"nome": "Reported speech", "sub": "said that, told me", "status": "nao_comecou"},
                {"nome": "Gerunds & infinitives", "sub": "-ing ou to + verbo?", "status": "nao_comecou"},
                {"nome": "Modals of deduction", "sub": "must, might, can't", "status": "nao_comecou"},
                {"nome": "Question tags", "sub": "..., isn't it?, don't you?", "status": "nao_comecou"},
                {"nome": "So / such", "sub": "tão, tanto", "status": "nao_comecou"}
            ]
        },
        "B2": {
            "titulo": "B2 · Intermediário Superior",
            "topicos": [
                {"nome": "Third & mixed conditionals", "sub": "o passado que não aconteceu", "status": "nao_comecou"},
                {"nome": "Should have / could have", "sub": "arrependimentos e críticas", "status": "nao_comecou"},
                {"nome": "Wish / if only", "sub": "desejos e arrependimentos", "status": "nao_comecou"},
                {"nome": "Advanced passive", "sub": "todos os tempos e modais", "status": "nao_comecou"},
                {"nome": "Have / get something done", "sub": "pedir para alguém fazer", "status": "nao_comecou"},
                {"nome": "Reported questions & commands", "sub": "asked if, told me to", "status": "nao_comecou"},
                {"nome": "Non-defining relative clauses", "sub": "informação extra entre vírgulas", "status": "nao_comecou"},
                {"nome": "Past modals of deduction", "sub": "must have, can't have", "status": "nao_comecou"},
                {"nome": "Future continuous & perfect", "sub": "will be doing, will have done", "status": "nao_comecou"},
                {"nome": "Used to / be used to / get used to", "sub": "hábito antigo x estar acostumada", "status": "nao_comecou"},
                {"nome": "Linking words of contrast", "sub": "although, despite, however", "status": "nao_comecou"},
                {"nome": "Participle clauses", "sub": "Walking home, I saw...", "status": "nao_comecou"}
            ]
        }
    }

    # ================= VISUALIZAÇÃO DA LIÇÃO / TÓPICO =================
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

        # A IDEIA
        st.markdown('<div class="section-tag">A IDEIA</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="info-box-light">
                Usamos o <b>to be</b> para dizer quem somos, de onde somos, nossa idade, profissão, como estamos e onde estamos.
                Em português temos dois verbos (ser e estar); em inglês, um só faz os dois papéis. Ele muda conforme a pessoa:
                <b style="color:{COR_MARCA_ESCURA};">am</b> com I, <b style="color:{COR_MARCA_ESCURA};">is</b> com he/she/it e <b style="color:{COR_MARCA_ESCURA};">are</b> com you/we/they.
            </div>
        """, unsafe_allow_html=True)

        # ESTRUTURA
        st.markdown('<div class="section-tag">ESTRUTURA</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="info-box-light">
                <div class="struct-row"><span class="struct-symbol">+</span><span>I <b>am</b> (I'm) &nbsp;·&nbsp; he/she/it <b>is</b> (she's) &nbsp;·&nbsp; you/we/they <b>are</b> (we're)</span></div>
                <div class="struct-row"><span class="struct-symbol">-</span><span>I'm <b>not</b> &nbsp;·&nbsp; she <b>isn't</b> &nbsp;·&nbsp; they <b>aren't</b></span></div>
                <div class="struct-row"><span class="struct-symbol">?</span><span><b>Am</b> I...? &nbsp;·&nbsp; <b>Is</b> he...? &nbsp;·&nbsp; <b>Are</b> you...?</span></div>
                <div class="struct-row"><span class="struct-symbol">✓</span><span>Respostas curtas: Yes, I <b>am</b>. / No, she <b>isn't</b>.</span></div>
            </div>
        """, unsafe_allow_html=True)

        # EXEMPLOS
        st.markdown('<div class="section-tag">EXEMPLOS</div>', unsafe_allow_html=True)
        st.caption("Toque na frase para ver a tradução")
        ex1, ex2 = st.columns(2)
        with ex1:
            st.info("I **am** 14 years old.  \n*(Eu tenho 14 anos de idade.)*")
            st.info("We **aren't** tired. We're excited!  \n*(Nós não estamos cansados. Estamos empolgados!)*")
        with ex2:
            st.info("My best friend **is** from Curitiba.  \n*(O meu melhor amigo é de Curitiba.)*")
            st.info("**Is** your mom a teacher? – Yes, she **is**.  \n*(A tua mãe é professora? – Sim, é.)*")

        # DICAS E ERROS COMUNS
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

        # ================= SEÇÃO PRATIQUE =================
        st.markdown('<div class="section-tag">PRATIQUE</div>', unsafe_allow_html=True)
        st.markdown("### Exercícios interativos")
        st.caption("Clique nas opções abaixo ou preencha os campos para conferir.")

        if "respostas_submetidas" not in st.session_state:
            st.session_state.respostas_submetidas = {}

        acertos_atuais = sum(1 for k, v in st.session_state.respostas_submetidas.items() if v == "correto")
        st.markdown(f"**{acertos_atuais} / 5 acertos**")
        st.progress(acertos_atuais / 5)
        st.markdown("<br>", unsafe_allow_html=True)

        # --- QUESTÃO 1 ---
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

        # --- QUESTÃO 2 ---
        status_q2 = st.session_state.respostas_submetidas.get("q2", None)
        if status_q2 == "correto":
            st.markdown('<div class="ex-card-correct">2. ___ you hungry?<br><br>✅ <b>Isso!</b> Pergunta com <i>you</i> → Are.</div>', unsafe_allow_html=True)
        elif status_q2 == "errado":
            st.markdown('<div class="ex-card-wrong">2. ___ you hungry?<br><br>❌ <b>Incorreto.</b> A resposta certa é <b>Are</b>.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ex-card-neutral">2. ___ you hungry?</div>', unsafe_allow_html=True)
