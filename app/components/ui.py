"""
Componentes de UI reutilizáveis para o Spotify Rewind App.
"""

import streamlit as st
import pandas as pd

from app.config import (
    COLORS,
    TABS,
    DEFAULT_TOP_N,
    inject_custom_css,
)


def render_header():
    """Header principal com gradiente verde."""
    st.markdown(
        """
        <h1 class="header-title">🎵 Spotify Rewind</h1>
        <p class="header-subtitle">
            Sua jornada musical — análises completas do seu histórico do Spotify
        </p>
        <hr style="border: 0; height: 1px; background: linear-gradient(90deg, transparent, #1DB954, transparent); margin: 16px 0 24px;">
        """,
        unsafe_allow_html=True,
    )


def render_upload_section():
    """Área de upload do ZIP com instruções."""
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "📁 Faça upload do seu arquivo ZIP do Spotify",
            type=["zip"],
            help="Baixe seus dados em https://www.spotify.com/br/account/privacy/",
        )
    with col2:
        st.info(
            "🔍 **Como obter seus dados**\n\n"
            "1. Acesse [Spotify Privacy](https://www.spotify.com/br/account/privacy/)\n"
            "2. Solicite 'Spotify Extended Streaming History'\n"
            "3. Faça upload do ZIP recebido aqui",
            icon="📋",
        )
    return uploaded


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    """
    Renderiza filtros na sidebar.
    Retorna dicionário com anos, artistas, query, top_n, metric selecionados.
    """
    with st.sidebar:
        st.markdown(
            f"<h3 style='color: {COLORS['primary']};'>🔍 Filtros</h3>",
            unsafe_allow_html=True,
        )

        # Anos
        available_years = sorted(df["year"].unique(), reverse=True)
        years = st.multiselect(
            "Ano",
            options=available_years,
            default=available_years,
            help="Selecione um ou mais anos para filtrar",
        )

        # Artistas
        artists_sorted = sorted(df["artist"].unique())
        artists = st.multiselect(
            "Artista",
            options=artists_sorted,
            help="Filtre por artista(s) específico(s)",
        )

        # Busca
        search_query = st.text_input(
            "🔎 Buscar música/artista",
            placeholder="Ex: bossa nova, Chico Buarque...",
            help="Busca por nome da música ou artista",
        ).strip()

        st.markdown("---")
        st.markdown(
            f"<h3 style='color: {COLORS['primary']};'>⚙️ Opções</h3>",
            unsafe_allow_html=True,
        )

        # Top N
        top_n = st.slider(
            "Top N artistas/músicas",
            min_value=5,
            max_value=50,
            value=DEFAULT_TOP_N,
        )

        # Métrica
        metric = st.radio(
            "Ordenar por", ["minutos", "plays"], horizontal=True
        )

        st.markdown("---")
        # Estatísticas rápidas
        st.markdown(
            f"<h4 style='color: {COLORS['muted']};'>📊 Dados carregados</h4>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Streams:** {len(df):,}")
        st.markdown(f"**Músicas únicas:** {df['track_name'].nunique():,}")
        st.markdown(f"**Artistas únicos:** {df['artist'].nunique():,}")
        total_h = df["minutes_played"].sum() / 60
        st.markdown(f"**Horas:** {total_h:,.1f}h")

        # Limpar filtros
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            st.rerun()

        # Carregar outro arquivo ZIP
        if st.button("📁 Carregar Outro Arquivo", use_container_width=True):
            st.session_state.df = None
            st.session_state.df_loaded = False
            st.rerun()

    return {
        "years": years,
        "artists": artists,
        "search_query": search_query,
        "top_n": top_n,
        "metric": metric,
    }


def render_metric_card(value: str, label: str, col):
    """Card de métrica estilizada como Spotify."""
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_stats_row(stats: dict):
    """Linha de cards com métricas globais."""
    c1, c2, c3, c4 = st.columns(4)

    # Total de minutos formatado
    if stats["total_minutes"] >= 60000:
        total_str = f"{stats['total_minutes']/60000:.1f}M"
    elif stats["total_minutes"] >= 1000:
        total_str = f"{stats['total_minutes']/1000:.1f}K"
    else:
        total_str = f"{stats['total_minutes']:,.0f}"

    render_metric_card(f"{stats['total_streams']:,}", "Streams Totais", c1)
    render_metric_card(f"{total_str}", "Minutos Ouvidos", c2)
    render_metric_card(f"{stats['unique_tracks']:,}", "Músicas Únicas", c3)
    render_metric_card(f"{stats['unique_artists']:,}", "Artistas Únicos", c4)

    c5, c6, c7, c8 = st.columns(4)
    render_metric_card(f"{stats['avg_daily_minutes']:.0f}", "Média Min/Dia", c5)

    # Período
    period = f"{stats['first_date']} → {stats['last_date']}"
    period_str = f"{stats['year_range'][0]}-{stats['year_range'][1]}"
    render_metric_card(period_str, "Período (anos)", c6)

    # Pico horário
    render_metric_card(f"{stats['peak_hour']}h", "Horário de Pico", c7)

    # Top artista
    top_artist_short = stats["top_artist"][:18] + "..." if len(stats["top_artist"]) > 20 else stats["top_artist"]
    render_metric_card(top_artist_short, "🎤 Artista Top", c8)


def render_tab_navigation() -> str:
    """Renderiza tabs de navegação e retorna a aba ativa."""
    tab_labels = [f"{emoji} {label}" for emoji, label in TABS]
    tabs = st.tabs(tab_labels)
    return tabs


def render_footer():
    """Footer estilizado."""
    st.markdown("---")
    st.markdown(
        f"""
        <div class="footer">
            🎵 <b>Spotify Rewind</b> — Análise do seu histórico musical &middot;
            Dados do <a href="https://www.spotify.com/br/account/privacy/"
            style="color: {COLORS['primary']}; text-decoration: none;">Spotify Extended Streaming History</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_loading_state():
    """Spinner de carregamento enquanto dados são processados."""
    placeholder = st.empty()
    return placeholder


def render_empty_state():
    """Estado vazio — nenhum dado carregado."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 80px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">🎵</div>
            <h2 style="color: {COLORS['muted']};">Bem-vindo ao Spotify Rewind!</h2>
            <p style="color: {COLORS['muted']}; font-size: 18px;">
                Faça upload do seu arquivo ZIP com os dados do Spotify 
                para começar a análise.
            </p>
            <p style="color: #555; font-size: 14px;">
                Você pode baixar seus dados em 
                <a href="https://www.spotify.com/br/account/privacy/" 
                   style="color: {COLORS['primary']}; text-decoration: none;">
                    spotify.com/account/privacy
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
