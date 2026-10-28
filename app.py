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
        st.markdown('<div class="metric-card"><h3>0</h3><p style="color: #6b7a90; margin:0;">Praticados</p></div>', unsafe_allow_html=True)
    with col_v3:
        st.markdown('<div class="metric-card"><h3>0</h3><p style="color: #6b7a90; margin:0;">Dominados</p></div>', unsafe_allow_html=True)
    with col_v4:
        st.markdown('<div class="metric-card"><h3>0%</h3><p style="color: #6b7a90; margin:0;">Taxa de Acerto</p></div>', unsafe_allow_html=True)

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

            # URLs oficiais de áudio do Google Translate (geram o som em MP3 nativo da palavra)
            url_inf = f"https://translate.google.com/translate_tts?ie=UTF-8&q={inf}&tl=en&client=tw-ob"
            url_past = f"https://translate.google.com/translate_tts?ie=UTF-8&q={past}&tl=en&client=tw-ob"
            url_part = f"https://translate.google.com/translate_tts?ie=UTF-8&q={part}&tl=en&client=tw-ob"

            card_html = f"""
            <div class="verb-card">
                <span style="background-color: #fdf2f8; color: #db2777; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; float: right;">{pat}</span>
                
                <h3 style="margin:0; color:#1e293b;">
                    {inf} 
                    <audio id="player_inf_{i}" src="{url_inf}"></audio>
                    <span style="cursor:pointer; font-size:16px;" onclick="document.getElementById('player_inf_{i}').play()" title="Ouvir">🔊</span>
                </h3>
                
                <p style="color:#64748b; font-size:13px; margin:2px 0 0 0;">{fon}</p>
                <hr style="margin:10px 0; border-top:1px solid #f1f5f9;">
                
                <div style="display:flex; justify-content:space-between; font-size:13px;">
                    <div>
                        <b>Past Simple:</b><br>
                        <span style="color:#4f67e8;">{past}</span>
                        <audio id="player_past_{i}" src="{url_past}"></audio>
                        <span style="cursor:pointer;" onclick="document.getElementById('player_past_{i}').play()" title="Ouvir">🔊</span><br>
                        <span style="color:#94a3b8; font-size:11px;">{past_fon}</span>
                    </div>
                    <div>
                        <b>Past Participle:</b><br>
                        <span style="color:#4f67e8;">{part}</span>
                        <audio id="player_part_{i}" src="{url_part}"></audio>
                        <span style="cursor:pointer;" onclick="document.getElementById('player_part_{i}').play()" title="Ouvir">🔊</span><br>
                        <span style="color:#94a3b8; font-size:11px;">{part_fon}</span>
                    </div>
                </div>
                
                <p style="margin:12px 0 4px 0; font-size:13px;"><b>Tradução:</b> {trans}</p>
                <p style="margin:0; font-size:12px; color:#64748b; font-style:italic;">Exemplo: {ex}</p>
            </div>
            """
            with cols[i % 3]:
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("Nenhum verbo encontrado com os filtros selecionados.")
