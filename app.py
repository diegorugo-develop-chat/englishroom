import json
import gspread
import pandas as pd
import streamlit as st
from datetime import datetime

# ======================= CONFIGURAÇÕES =======================
PLANILHA_ID = "1AhC0DeQFA1tQyrT3ldvDun_jy2DC-Dur3WF_yOBf4qQ"
NOME_ABA_USUARIOS = "usuarios"
NOME_ABA_PROGRESSO = "progresso"
NOME_ABA_VERBOS = "verbos_irregulares"

st.set_page_config(
    page_title="CarolEnglish — Plataforma de Ensino",
    page_icon="💜",
    layout="wide"
)

# ======================= ESTILOS CSS =======================
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f6fc;
            font-family: 'Inter', sans-serif;
        }
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

# Script JavaScript global para síntese de voz nativa do navegador (Web Speech API)
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
        st.error(f"Erro ao ler a aba de usuários: {e}")
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
            st.session_state.niveis = dados["niveis"]
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
    st.session_state.niveis = {}
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


# ======================= SISTEMA PRINCIPAL =======================

dados_progresso = carregar_progresso_usuario(st.session_state.usuario)

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("### 💜 CarolEnglish")
    st.caption(f"Aluno(a): **{st.session_state.nome}**")
    
    niveis_ativos = [nv for nv, status in st.session_state.niveis.items() if status == "SIM"]
    st.caption(f"Níveis Autorizados: **{', '.join(niveis_ativos) if niveis_ativos else 'Nenhum'}**")
    st.divider()

    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dashboard" else "secondary"):
        st.session_state.pagina_atual = "dashboard"
        st.rerun()

    if st.button("🚀 Skills / Trilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "skills" else "secondary"):
        st.session_state.pagina_atual = "skills"
        st.rerun()

    if st.button("🔄 Verbos Irregulares", use_container_width=True, type="primary" if st.session_state.pagina_atual == "verbs" else "secondary"):
        st.session_state.pagina_atual = "verbs"
        st.rerun()

    if st.button("💬 Practice & AI", use_container_width=True, type="primary" if st.session_state.pagina_atual == "practice" else "secondary"):
        st.session_state.pagina_atual = "practice"
        st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 Sair / Logout", type="secondary", use_container_width=True):
        realizar_logout()


# --- CORTE DE PÁGINAS ---
pagina = st.session_state.pagina_atual

if pagina == "dashboard":
    st.markdown(f"""
        <div class="welcome-banner">
            <h2>Dashboard · Bem-vindo(a), {st.session_state.nome}!</h2>
            <p style="margin: 0; opacity: 0.9;">Continue mantendo sua sequência de estudos em dia ✨</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["xp"]}</h3><p style="color: #6b7a90; margin:0;">Points / XP</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["streak"]}</h3><p style="color: #6b7a90; margin:0;">Streak 🔥</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["gems"]}</h3><p style="color: #6b7a90; margin:0;">Gems 💎</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><h3>{dados_progresso["licoes_concluidas"]}</h3><p style="color: #6b7a90; margin:0;">Lições Concluídas 🏆</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚡ Ações Rápidas de Estudo")
    if st.button("✅ Concluir Lição de Exemplo (+50 XP e +10 Gems)"):
        atualizar_progresso_no_sheets(st.session_state.usuario, xp_add=50, gems_add=10, licoes_add=1)
        st.success("Parabéns! Sua atividade foi registrada e salva no Google Sheets com sucesso!")
        st.rerun()

elif pagina == "skills":
    st.title("🚀 Skills & Trilha de Aprendizado")
    if st.session_state.niveis.get("A1") == "SIM":
        st.markdown('<div class="content-card"><h4>📖 Módulo Iniciante (Nível A1)</h4><p>Conteúdos básicos liberados para o seu aprendizado.</p></div>', unsafe_allow_html=True)
    if st.session_state.niveis.get("A2") == "SIM":
        st.markdown('<div class="content-card"><h4>📖 Módulo Elementar (Nível A2)</h4><p>Estruturas e vocabulário intermediário inicial.</p></div>', unsafe_allow_html=True)
    if st.session_state.niveis.get("B1") == "SIM":
        st.markdown('<div class="content-card"><h4>📖 Módulo Intermediário (Nível B1)</h4><p>Conversação fluida e gramática.</p></div>', unsafe_allow_html=True)

elif pagina == "verbs":
    st.title("Irregular Verbs")
    st.caption("Lista completa de 144 verbos irregulares organizados por padrões de transformação")
    st.markdown("<br>", unsafe_allow_html=True)

    verbos_lista = carregar_verbos_irregulares()
    total_verbos = len(verbos_lista)

    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    with col_v1:
        st.markdown(f'<div class="metric-card"><h3>{total_verbos}</h3><p style="color: #6b7a90; margin:0;">Total de Verbos</p></div>', unsafe_allow_html=True)
    with col_v2:
        st.markdown(f'<div class="metric-card"><h3>0</h3><p style="color: #6b7a90; margin:0;">Praticados</p></div>', unsafe_allow_html=True)
    with col_v3:
        st.markdown(f'<div class="metric-card"><h3>0</h3><p style="color: #6b7a90; margin:0;">Dominados</p></div>', unsafe_allow_html=True)
    with col_v4:
        st.markdown(f'<div class="metric-card"><h3>0%</h3><p style="color: #6b7a90; margin:0;">Taxa de Acerto</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    padroes_disponiveis = ["Todos os padrões"] + sorted(list({str(v.get("pattern", "")).strip() for v in verbos_lista if v.get("pattern")}))

    with st.container():
        st.markdown("### Filtros")
        st.caption("Filtre verbos por padrão ou busque por texto")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            filtro_padrao = st.selectbox("Padrão", padroes_disponiveis)
        with f_col2:
            busca_texto = st.text_input("Buscar", placeholder="Digite infinitivo, passado ou tradução...")

    st.markdown("<br>", unsafe_allow_html=True)

    verbos_filtrados = verbos_lista
    if filtro_padrao != "Todos os padrões":
        verbos_filtrados = [v for v in verbos_filtrados if str(v.get("pattern", "")).strip() == filtro_padrao]
    if busca_texto:
        bt = busca_texto.lower()
        verbos_filtrados = [
            v for v in verbos_filtrados 
            if bt in str(v.get("infinitive", "")).lower() 
            or bt in str(v.get("past", "")).lower() 
            or bt in str(v.get("translation", "")).lower()
        ]

    if verbos_filtrados:
        cols = st.columns(3)
        for i, verb in enumerate(verbos_filtrados):
            inf = str(verb.get("infinitive", ""))
            fon = str(verb.get("phonetic", ""))
            past = str(verb.get("past", ""))
            past_fon = str(verb.get("past_phonetic", ""))
            part = str(verb.get("participle", ""))
            part_fon = str(verb.get("part_phonetic", ""))
            trans = str(verb.get("translation", ""))
            ex = str(verb.get("example", ""))
            pat = str(verb.get("pattern", ""))

            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**Padrão:** `{pat}`")
                    
                    # Cabeçalho do verbo com botão de áudio seguro
                    c_inf1, c_inf2 = st.columns([3, 1])
                    with c_inf1:
                        st.markdown(f"### {inf}")
                    with c_inf2:
                        st.markdown(f'<button onclick="falar(\'{inf}\')" style="background:#f0f3ff; color:#4f67e8; border:none; border-radius:8px; padding:6px 10px; cursor:pointer; font-weight:600;">🔊 Ouvir</button>', unsafe_allow_html=True)
                            
                    st.caption(fon)
                    st.divider()
                    
                    # Past Simple e Past Participle
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("**Past Simple:**")
                        st.markdown(f"<span style='color:#4f67e8; font-weight:600;'>{past}</span>", unsafe_allow_html=True)
                        st.caption(past_fon)
                        st.markdown(f'<button onclick="falar(\'{past}\')" style="background:#f0f3ff; color:#4f67e8; border:none; border-radius:6px; padding:4px 8px; cursor:pointer; font-size:11px; font-weight:600;">🔊 Ouvir</button>', unsafe_allow_html=True)
                            
                    with col_p2:
                        st.markdown("**Past Participle:**")
                        st.markdown(f"<span style='color:#4f67e8; font-weight:600;'>{part}</span>", unsafe_allow_html=True)
                        st.caption(part_fon)
                        st.markdown(f'<button onclick="falar(\'{part}\')" style="background:#f0f3ff; color:#4f67e8; border:none; border-radius:6px; padding:4px 8px; cursor:pointer; font-size:11px; font-weight:600;">🔊 Ouvir</button>', unsafe_allow_html=True)
                        
                    st.divider()
                    st.markdown(f"**Tradução:** {trans}")
                    st.markdown(f"*Exemplo:* {ex}")
    else:
        st.info("Nenhum verbo encontrado com os filtros selecionados.")

elif pagina == "practice":
    st.title("💬 Prática com Inteligência Artificial")
    st.info("Inicie conversas e simulações para treinar conversação e escrita de acordo com o seu nível.")
