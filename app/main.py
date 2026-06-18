"""
Spotify Rewind — Orquestrador Principal.

App Streamlit modular para análise do histórico do Spotify.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from app.config import (
    PAGE_CONFIG,
    TABS,
    COLORS,
    DEV_MODE,
    DEV_DATA_PATH,
    inject_custom_css,
)
from app.components.ui import (
    render_header,
    render_upload_section,
    render_sidebar_filters,
    render_stats_row,
    render_footer,
    render_empty_state,
)
from app.components.charts import (
    create_yearly_bar,
    create_monthly_comparison_chart,
    create_hourly_chart,
    create_weekly_chart,
    create_heatmap,
    create_top_tracks_by_artist_chart,
    create_top_artists_chart,
    create_artist_evolution_chart,
    create_session_histogram,
    create_platform_pie,
    create_platform_trends_chart,
    create_styled_table,
)
from app.components.advanced_charts import (
    create_emoji_wordcloud,
    create_listening_heatmap,
    create_sunburst_chart,
    create_genre_treemap,
    create_top_artists_ranking,
    create_monthly_evolution,
    create_artist_network,
    create_bar_chart_race,
)

from src.data_loader import load_data_from_bytes, load_data_from_directory
from src.data_processor import (
    apply_filters,
    compute_global_stats,
    get_yearly_stats,
    get_monthly_comparison,
    get_hourly_distribution,
    get_weekly_distribution,
    get_heatmap_data,
    get_top_tracks,
    get_top_artists,
    get_artist_evolution,
    get_session_analysis,
    get_platform_distribution,
    get_platform_trends,
)


# ---------------------------------------------------------------------------
# Configuração da página (executa uma vez)
# ---------------------------------------------------------------------------
st.set_page_config(**PAGE_CONFIG)
inject_custom_css()


# ---------------------------------------------------------------------------
# Estado da sessão: mantém DataFrame em cache entre interações
# ---------------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "df_loaded" not in st.session_state:
    st.session_state.df_loaded = False


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
render_header()


# ---------------------------------------------------------------------------
# Carregamento de dados
# ---------------------------------------------------------------------------
if DEV_MODE and not st.session_state.df_loaded:
    with st.spinner("🔄 Modo DEV: carregando dados locais..."):
        try:
            st.session_state.df = load_data_from_directory(DEV_DATA_PATH)
            st.session_state.df_loaded = True
            st.success(f"✅ Dados carregados — {len(st.session_state.df):,} streams de {st.session_state.df['year'].min()} a {st.session_state.df['year'].max()}")
        except Exception as e:
            st.error(f"Erro ao carregar dados locais: {e}")
            st.info("Desative DEV_MODE ou ajuste DEV_DATA_PATH em app/config.py")

elif not DEV_MODE and not st.session_state.df_loaded:
    uploaded = render_upload_section()

    if uploaded is not None:
        with st.spinner("📦 Processando ZIP..."):
            try:
                st.session_state.df = load_data_from_bytes(uploaded.read())
                st.session_state.df_loaded = True
                st.success(
                    f"✅ Dados carregados — {len(st.session_state.df):,} streams "
                    f"de {st.session_state.df['year'].min()} a {st.session_state.df['year'].max()}"
                )
                # Recarrega a página para exibir as análises imediatamente
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {e}")
                st.info(
                    "Verifique se o arquivo ZIP contém os JSONs "
                    "'Streaming_History_Audio_*.json' (Extended Streaming History) "
                    "ou 'StreamingHistory*.json' (Account Data)."
                )


# ---------------------------------------------------------------------------
# Se não tem dados, mostra estado vazio
# ---------------------------------------------------------------------------
if st.session_state.df is None:
    render_empty_state()
    st.stop()


# ---------------------------------------------------------------------------
# Filtros na sidebar
# ---------------------------------------------------------------------------
df = st.session_state.df
filters = render_sidebar_filters(df)

# Aplicar filtros
df_filtered = apply_filters(
    df,
    years=filters["years"],
    artists=filters["artists"],
    search_query=filters["search_query"],
)

# Verificar se filtros retornaram vazio
if df_filtered.empty:
    st.warning("⚠️ Nenhum resultado para os filtros selecionados. Tente ajustar os filtros.")
    st.stop()

# Atualizar estatísticas com filtered
stats = compute_global_stats(df_filtered)
top_n = filters["top_n"]
metric = filters["metric"]


# ---------------------------------------------------------------------------
# Tabs — cada aba é uma seção de análise
# ---------------------------------------------------------------------------
tab_visao, tab_tendencias, tab_musicas, tab_artistas, tab_sessoes, tab_plataforma, tab_avancado, tab_sobre = st.tabs(
    [f"{emoji} {label}" for emoji, label in TABS]
)


# ── TAB 1: Visão Geral ─────────────────────────────────────────────────────
with tab_visao:
    st.subheader("📊 Visão Geral")

    # Linha de métricas
    render_stats_row(stats)

    st.markdown("---")

    # Dois gráficos lado a lado
    col1, col2 = st.columns(2)

    with col1:
        yearly = get_yearly_stats(df_filtered)
        if not yearly.empty:
            fig_yearly = create_yearly_bar(yearly)
            st.plotly_chart(fig_yearly, use_container_width=True)

    with col2:
        hourly = get_hourly_distribution(df_filtered)
        if not hourly.empty:
            fig_hourly = create_hourly_chart(hourly)
            st.plotly_chart(fig_hourly, use_container_width=True)

    # Segunda linha: dia da semana + heatmap
    col3, col4 = st.columns(2)

    with col3:
        weekly = get_weekly_distribution(df_filtered)
        if not weekly.empty:
            fig_weekly = create_weekly_chart(weekly)
            st.plotly_chart(fig_weekly, use_container_width=True)

    with col4:
        heatmap_df = get_heatmap_data(df_filtered)
        if not heatmap_df.empty:
            fig_heat = create_heatmap(heatmap_df)
            st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_visao")

    # Resumo em tabela
    st.markdown("---")
    st.subheader("🎯 Principais Métricas")

    summary_data = {
        "Métrica": [
            "Artista Mais Ouvido",
            "Música Mais Tocada",
            "Horário de Pico",
            "Dia de Pico",
            "Total de Horas",
            "Média Diária",
        ],
        "Valor": [
            stats["top_artist"],
            f"{stats['top_track_name']} — {stats['top_track_artist']}",
            f"{stats['peak_hour']}h",
            stats["peak_day"],
            f"{stats['total_hours']:,.1f}h",
            f"{stats['avg_daily_minutes']:.0f} min/dia",
        ],
    }
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
    )


# ── TAB 2: Tendências ──────────────────────────────────────────────────────
with tab_tendencias:
    st.subheader("📈 Tendências Temporais")

    # Comparação mensal entre anos
    monthly_comp = get_monthly_comparison(df_filtered)
    if not monthly_comp.empty:
        fig_monthly = create_monthly_comparison_chart(monthly_comp)
        st.plotly_chart(fig_monthly, use_container_width=True)

    # Heatmap
    st.markdown("---")
    heatmap_df2 = get_heatmap_data(df_filtered)
    if not heatmap_df2.empty:
        fig_heat2 = create_heatmap(heatmap_df2)
        st.plotly_chart(fig_heat2, use_container_width=True, key="heatmap_tendencias")

    # Evolução dos artistas
    artist_evol = get_artist_evolution(df_filtered, top_n=min(10, top_n))
    if not artist_evol.empty:
        st.markdown("---")
        fig_evol = create_artist_evolution_chart(artist_evol)
        st.plotly_chart(fig_evol, use_container_width=True, key="evol_tendencias")

    # Tabela de minutos por ano
    st.markdown("---")
    yearly_table = get_yearly_stats(df_filtered)
    if not yearly_table.empty:
        yearly_table["Horas"] = (yearly_table["Minutos"] / 60).round(1)
        st.dataframe(
            yearly_table.style.format({"Minutos": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
            column_config={
                "year": "Ano",
                "Minutos": st.column_config.NumberColumn("Minutos", format="%d"),
                "Horas": st.column_config.NumberColumn("Horas"),
            },
        )


# ── TAB 3: Músicas ─────────────────────────────────────────────────────────
with tab_musicas:
    st.subheader("🎵 Top Músicas")

    col_metric, col_n = st.columns([1, 3])
    with col_metric:
        topn_tracks = st.slider(
            "Quantas músicas mostrar?",
            min_value=5,
            max_value=50,
            value=min(20, top_n),
            key="topn_tracks",
        )
    with col_n:
        metric_track = st.radio(
            "Ordenar por",
            ["plays", "minutes"],
            horizontal=True,
            format_func=lambda x: "Vezes tocada" if x == "plays" else "Minutos ouvidos",
            key="metric_track",
        )

    top_tracks = get_top_tracks(df_filtered, n=topn_tracks, metric=metric_track)

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        fig_tracks = create_top_tracks_by_artist_chart(top_tracks)
        st.plotly_chart(fig_tracks, use_container_width=True)

    with col_table:
        st.dataframe(
            top_tracks.style.format(
                {"Vezes tocada": "{:,.0f}", "Minutos": "{:,.0f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    # Busca detalhada
    st.markdown("---")
    st.subheader("🔎 Buscar Música")

    search = st.text_input(
        "Digite o nome da música ou artista",
        placeholder="Ex: Imprevisto, Lagum...",
        key="search_track",
    )
    if search.strip():
        q = search.strip().lower()
        df_search = df[
            df["track_name"].str.lower().str.contains(q, na=False)
            | df["artist"].str.lower().str.contains(q, na=False)
        ]

        if not df_search.empty:
            search_stats = compute_global_stats(df_search)
            st.info(
                f"🎯 {len(df_search)} streams encontrados — "
                f"{search_stats['total_minutes']:,} minutos"
            )

            # Top artistas nessa busca
            search_artists = (
                df_search.groupby("artist")["minutes_played"]
                .sum()
                .nlargest(10)
                .reset_index()
            )
            search_artists.columns = ["Artista", "Minutos"]
            search_artists["Horas"] = (search_artists["Minutos"] / 60).round(1)

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                search_tracks = (
                    df_search.groupby(["track_name", "artist"])
                    .size()
                    .nlargest(10)
                    .reset_index(name="Plays")
                )
                search_tracks.columns = ["Música", "Artista", "Plays"]
                st.dataframe(search_tracks, use_container_width=True, hide_index=True)
            with col_s2:
                st.dataframe(search_artists, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum resultado para a busca.")


# ── TAB 4: Artistas ────────────────────────────────────────────────────────
with tab_artistas:
    st.subheader("👤 Top Artistas")

    top_artists_df = get_top_artists(df_filtered, n=top_n, metric=metric)
    fig_artists = create_top_artists_chart(top_artists_df)
    st.plotly_chart(fig_artists, use_container_width=True)

    # Tabela completa
    st.dataframe(
        top_artists_df.style.format(
            {"Minutos": "{:,.0f}", "Horas": "{:,.1f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    # WordCloud
    st.markdown("---")
    st.subheader("☁️ Nuvem de Artistas")

    if st.button("🎨 Gerar Nuvem de Artistas", use_container_width=True, key="btn_wc"):
        with st.spinner("Gerando nuvem de palavras..."):
            # Contagem de streams por artista para peso na nuvem
            artist_counts = df_filtered["artist"].value_counts().to_dict()

            wc = WordCloud(
                width=1200,
                height=500,
                background_color="#191414",
                colormap="Greens",
                max_words=150,
                min_font_size=10,
                max_font_size=120,
                prefer_horizontal=0.7,
            ).generate_from_frequencies(artist_counts)

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

    # Evolução anual
    evol = get_artist_evolution(df_filtered, top_n=min(10, top_n))
    if not evol.empty:
        st.markdown("---")
        st.subheader("📈 Evolução Anual dos Artistas")
        fig_evol2 = create_artist_evolution_chart(evol)
        st.plotly_chart(fig_evol2, use_container_width=True, key="evol_artistas")


# ── TAB 5: Sessões ─────────────────────────────────────────────────────────
with tab_sessoes:
    st.subheader("🔄 Análise de Sessões")

    st.markdown(
        "Sessões são agrupamentos de streams consecutivos com intervalo "
        "máximo de **30 minutos** entre eles."
        f"\n\n*(Apenas sessões com duração ≥ 10 min são consideradas.)*"
    )

    with st.spinner("Analisando sessões..."):
        sessions = get_session_analysis(df_filtered)

    if not sessions.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total de Sessões", len(sessions))
        with c2:
            st.metric("Duração Média", f"{sessions['session_duration'].mean():.0f} min")
        with c3:
            st.metric("Média de Músicas/Sessão", f"{sessions['tracks_played'].mean():.1f}")

        fig_sessions = create_session_histogram(sessions)
        st.plotly_chart(fig_sessions, use_container_width=True)

        # Top sessões por duração
        st.markdown("---")
        st.subheader("🔝 Maiores Sessões")

        top_sessions = sessions.nlargest(10, "session_duration")[
            ["start_time", "session_duration", "tracks_played", "total_minutes"]
        ].copy()
        top_sessions["start_time"] = top_sessions["start_time"].dt.strftime("%d/%m/%Y %H:%M")
        top_sessions["session_duration"] = top_sessions["session_duration"].round(1)
        top_sessions["total_minutes"] = top_sessions["total_minutes"].round(1)

        top_sessions.columns = [
            "Início", "Duração (min)", "Músicas", "Minutos Tocados"
        ]
        st.dataframe(top_sessions, use_container_width=True, hide_index=True)

    else:
        st.warning("Não foi possível identificar sessões.")


# ── TAB 6: Plataforma ──────────────────────────────────────────────────────
with tab_plataforma:
    st.subheader("📱 Distribuição por Plataforma")

    col1, col2 = st.columns(2)

    with col1:
        platform_dist = get_platform_distribution(df_filtered)
        if not platform_dist.empty:
            fig_platform = create_platform_pie(platform_dist)
            st.plotly_chart(fig_platform, use_container_width=True)

    with col2:
        platform_trends = get_platform_trends(df_filtered)
        if not platform_trends.empty:
            fig_trends = create_platform_trends_chart(platform_trends)
            st.plotly_chart(fig_trends, use_container_width=True)

    # Tabela
    if not platform_dist.empty:
        st.markdown("---")
        platform_table = platform_dist.reset_index()
        platform_table.columns = ["Plataforma", "Minutos"]
        platform_table["Horas"] = (platform_table["Minutos"] / 60).round(1)
        platform_table["%"] = (
            platform_table["Minutos"] / platform_table["Minutos"].sum() * 100
        ).round(1)

        st.dataframe(
            platform_table.style.format(
                {"Minutos": "{:,.0f}", "Horas": "{:,.1f}"}
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Plataforma": "Plataforma",
                "Minutos": st.column_config.NumberColumn("Minutos", format="%d"),
                "Horas": st.column_config.NumberColumn("Horas"),
                "%": st.column_config.NumberColumn("%", format="%.1f%%"),
            },
        )

    # País de conexão (se disponível)
    if "conn_country" in df_filtered.columns:
        st.markdown("---")
        st.subheader("🌍 Países de Conexão")
        country_dist = (
            df_filtered.groupby("conn_country")["minutes_played"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        country_dist.columns = ["País (Código)", "Minutos"]
        country_dist["Horas"] = (country_dist["Minutos"] / 60).round(1)
        st.dataframe(country_dist, use_container_width=True, hide_index=True)



# ── TAB 7: Análises Avançadas ───────────────────────────────────────────────
with tab_avancado:
    st.subheader("✨ Análises Avançadas e Visualizações Interativas")
    
    st.markdown("""
    Exploração profunda dos seus hábitos musicais com visualizações avançadas:
    **WordCloud**, **Heatmap**, **Sunburst**, **Treemap**, **Bar Chart Race**, **Rede de Artistas** e mais!
    """)
    
    # Abas internas para organizar as 8 visualizações
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6, sub_tab7, sub_tab8 = st.tabs([
        "☁️ WordCloud",
        "🔥 Heatmap",
        "🌳 Sunburst",
        "🎨 Treemap",
        "⭐ Top 20",
        "📈 Evolução",
        "🔗 Rede",
        "🏃 Race"
    ])
    
    # 1. WordCloud com Emoji
    with sub_tab1:
        st.subheader("☁️ Nuvem de Artistas")
        st.markdown("Visualização do tamanho dos artistas baseado no número de streams.")
        if st.button("🎨 Gerar WordCloud", key="btn_wc_advanced", use_container_width=True):
            with st.spinner("Gerando nuvem de palavras..."):
                create_emoji_wordcloud(df_filtered, top_n=50)
    
    # 2. Heatmap de Horários
    with sub_tab2:
        st.subheader("🔥 Heatmap de Audição")
        st.markdown("Padrão de audição por **hora do dia** e **dia da semana**.")
        with st.spinner("Gerando heatmap..."):
            fig_heatmap = create_listening_heatmap(df_filtered)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 3. Sunburst
    with sub_tab3:
        st.subheader("🌳 Sunburst: Artista → Música")
        st.markdown("Hierarquia interativa mostrando artistas e suas músicas mais tocadas.")
        top_n_sunburst = st.slider("Quantos artistas mostrar?", 5, 50, 20, key="sunburst_n")
        with st.spinner("Gerando sunburst..."):
            fig_sunburst = create_sunburst_chart(df_filtered, top_n=top_n_sunburst)
            st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # 4. Treemap
    with sub_tab4:
        st.subheader("🎨 Treemap de Artistas")
        st.markdown("Visualização proporcional do tempo ouvido por artista.")
        top_n_treemap = st.slider("Quantos artistas mostrar?", 5, 50, 25, key="treemap_n")
        with st.spinner("Gerando treemap..."):
            fig_treemap = create_genre_treemap(df_filtered, top_n=top_n_treemap)
            st.plotly_chart(fig_treemap, use_container_width=True)
    
    # 5. Top 20 Artistas com Ranking
    with sub_tab5:
        st.subheader("⭐ Ranking dos Top 20 Artistas")
        st.markdown("Ranking horizontal dos artistas mais ouvidos.")
        top_n_ranking = st.slider("Quantos artistas mostrar?", 5, 50, 20, key="ranking_n")
        with st.spinner("Gerando ranking..."):
            fig_ranking = create_top_artists_ranking(df_filtered, top_n=top_n_ranking)
            st.plotly_chart(fig_ranking, use_container_width=True)
    
    # 6. Evolução Mensal
    with sub_tab6:
        st.subheader("📈 Evolução Mensal de Minutos")
        st.markdown("Tendência de minutos ouvidos ao longo do tempo.")
        with st.spinner("Gerando gráfico de evolução..."):
            fig_evolution = create_monthly_evolution(df_filtered)
            st.plotly_chart(fig_evolution, use_container_width=True)
    
    # 7. Rede de Artistas
    with sub_tab7:
        st.subheader("🔗 Rede de Artistas")
        st.markdown("Visualização de rede mostrando co-ocorrências de artistas em suas sessões de audição.")
        top_n_network = st.slider("Quantos artistas mostrar?", 5, 50, 30, key="network_n")
        if st.button("🔍 Gerar Rede", key="btn_network", use_container_width=True):
            with st.spinner("Gerando rede de artistas (isso pode levar um tempo)..."):
                try:
                    html_network = create_artist_network(df_filtered, top_n=top_n_network)
                    if html_network:
                        st.components.v1.html(html_network, height=650, scrolling=True)
                except Exception as e:
                    st.error(f"Erro ao gerar rede: {e}")
                    st.info("Certifique-se de que pyvis e networkx estão instalados: `pip install pyvis networkx`")
    
    # 8. Bar Chart Race
    with sub_tab8:
        st.subheader("🏃 Bar Chart Race: Evolução dos Artistas")
        st.markdown("Animação mostrando como o ranking dos artistas evoluiu ao longo dos meses.")
        top_n_race = st.slider("Quantos artistas mostrar?", 5, 30, 15, key="race_n")
        with st.spinner("Gerando bar chart race..."):
            fig_race = create_bar_chart_race(df_filtered, top_n=top_n_race)
            st.plotly_chart(fig_race, use_container_width=True)
    
    # Seção de resumo
    st.markdown("---")
    st.markdown("""
    ### 🌟 Dicas para Explorar
    
    - **WordCloud**: Clique em "Gerar" para visualizar a nuvem de artistas
    - **Heatmap**: Identifique seus horários de pico de audição
    - **Sunburst**: Clique nos segmentos para explorar a hierarquia
    - **Treemap**: Veja o tamanho relativo de cada artista
    - **Ranking**: Classificação clara dos seus top artistas
    - **Evolução**: Acompanhe como seus hábitos mudam ao longo do tempo
    - **Rede**: Descubra quais artistas você ouve juntos
    - **Race**: Veja a competição entre artistas mês a mês
    """)


# ── TAB 8: Sobre ───────────────────────────────────────────────────────────
with tab_sobre:
    st.subheader("ℹ️ Sobre o Spotify Rewind")

    st.markdown(
        f"""
        <div style="background-color: {COLORS['secondary_bg']}; 
                    border-radius: 12px; padding: 24px; margin-bottom: 20px;
                    border: 1px solid #333;">
            <h3 style="color: {COLORS['primary']};">🎵 Spotify Rewind</h3>
            <p style="color: {COLORS['muted']};">
                Transforme seu histórico do Spotify em análises interativas.
            </p>
        </div>

        <div style="background-color: {COLORS['secondary_bg']}; 
                    border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            <h4 style="color: {COLORS['primary']};">📖 Sobre a Análise</h4>
            <p style="color: {COLORS['muted']}; line-height: 1.7;">
                Este app processa os dados do 
                <strong>Spotify Extended Streaming History</strong>, 
                fornecendo insights sobre seus hábitos de escuta. 
            </p>
            <ul style="color: {COLORS['muted']}; line-height: 1.7;">
                <li><strong>📊 Visão Geral</strong> — Métricas globais, resumo por ano, 
                    padrões por hora e dia da semana</li>
                <li><strong>📈 Tendências</strong> — Comparação mensal entre anos, 
                    heatmap, evolução dos artistas</li>
                <li><strong>🎵 Músicas</strong> — Top músicas, busca detalhada</li>
                <li><strong>👤 Artistas</strong> — Top artistas, nuvem de palavras, 
                    evolução anual</li>
                <li><strong>🔄 Sessões</strong> — Análise de padrões de escuta</li>
                <li><strong>📱 Plataforma</strong> — Distribuição por dispositivo</li>
            </ul>
        </div>

        <div style="background-color: {COLORS['secondary_bg']}; 
                    border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            <h4 style="color: {COLORS['primary']};">🔒 Privacidade</h4>
            <p style="color: {COLORS['muted']}; line-height: 1.7;">
                Seus dados <strong>não saem do seu computador</strong>. 
                Todo o processamento é local. Nenhum dado é enviado para servidores externos.
            </p>
        </div>

        <div style="background-color: {COLORS['secondary_bg']}; 
                    border-radius: 12px; padding: 24px;">
            <h4 style="color: {COLORS['primary']};">🛠️ Stack Técnica</h4>
            <p style="color: {COLORS['muted']};">
                Python, Streamlit, Pandas, Plotly, Matplotlib, WordCloud
            </p>
            <p style="color: #555; font-size: 12px;">
                Versão 1.0
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
render_footer()
