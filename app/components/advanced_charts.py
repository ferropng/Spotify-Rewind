"""
Módulo de visualizações avançadas do Spotify Rewind.
Inclui: WordCloud com emoji, Heatmap, Sunburst, Treemap, Bar Chart Race, Rede de Artistas, etc.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st

from app.config import COLORS, DAY_ORDER, DAY_LABELS, MONTH_LABELS, MONTH_NUM_TO_LABEL


def _dark_template():
    """Template escuro customizado."""
    return go.layout.Template(
        layout=go.Layout(
            plot_bgcolor=COLORS["background"],
            paper_bgcolor=COLORS["background"],
            font=dict(color=COLORS["text"]),
        )
    )


# ─── 1. WordCloud com Emoji ────────────────────────────────────────────────

def create_emoji_wordcloud(df: pd.DataFrame) -> None:
    """Gera WordCloud dos artistas mais ouvidos."""
    top_artists = df["artist"].value_counts().head(30)

    if top_artists.empty:
        st.warning("Sem dados para gerar WordCloud.")
        return

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color=COLORS["background"],
        colormap="Greens",
        relative_scaling=0.5,
        min_font_size=10,
    ).generate_from_frequencies(top_artists)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=COLORS["background"])
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, use_container_width=True)


# ─── 2. Heatmap de Audição ─────────────────────────────────────────────────

def create_listening_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap: hora do dia vs dia da semana."""
    heatmap_data = df.groupby(["hour", "day_of_week"]).size().reset_index(name="plays")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data["day_of_week"] = pd.Categorical(
        heatmap_data["day_of_week"], categories=day_order, ordered=True
    )
    heatmap_pivot = heatmap_data.pivot(index="hour", columns="day_of_week", values="plays").fillna(0)

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale="Greens",
            name="Plays",
        )
    )

    fig.update_layout(
        title="Padrão de Audição (Hora vs Dia da Semana)",
        xaxis_title="Dia da Semana",
        yaxis_title="Hora do Dia",
        height=500,
        template="plotly_dark",
        hovermode="closest",
    )

    return fig


# ─── 3. Sunburst: Artista → Música ────────────────────────────────────────

def create_sunburst_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Sunburst interativo: Artista → Música."""
    top_artists = df["artist"].value_counts().head(top_n).index
    df_top = df[df["artist"].isin(top_artists)]

    sunburst_data = (
        df_top.groupby(["artist", "track_name"])["minutes_played"]
        .sum()
        .reset_index()
        .sort_values("minutes_played", ascending=False)
    )

    # Construir estrutura hierárquica: raiz → artistas → músicas
    # Nós de artista (pais: raiz)
    artist_rows = []
    for artist in top_artists:
        artist_rows.append({
            "id": artist,
            "label": artist,
            "parent": "",
            "value": sunburst_data[sunburst_data["artist"] == artist]["minutes_played"].sum(),
        })

    # Nós de música (pais: artista)
    music_rows = []
    for _, row in sunburst_data.iterrows():
        music_rows.append({
            "id": f"{row['artist']} - {row['track_name']}",
            "label": row["track_name"],
            "parent": row["artist"],
            "value": row["minutes_played"],
        })

    # Combinar em um DataFrame
    hierarchy_df = pd.DataFrame(artist_rows + music_rows)

    fig = px.sunburst(
        hierarchy_df,
        ids="id",
        labels="label",
        parents="parent",
        values="value",
        color="value",
        color_continuous_scale="Greens",
        title=f"Hierarquia: Top {top_n} Artistas → Músicas",
    )

    fig.update_layout(height=600, template="plotly_dark")
    return fig


# ─── 4. Treemap de Artistas ────────────────────────────────────────────────

def create_genre_treemap(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Treemap proporcional dos artistas."""
    top_artists = df["artist"].value_counts().head(top_n).index
    df_top = df[df["artist"].isin(top_artists)]

    treemap_data = (
        df_top.groupby("artist")["minutes_played"]
        .sum()
        .reset_index()
        .sort_values("minutes_played", ascending=False)
    )

    fig = px.treemap(
        treemap_data,
        values="minutes_played",
        names="artist",
        color="minutes_played",
        color_continuous_scale="Greens",
        title=f"Treemap: Top {top_n} Artistas",
    )

    fig.update_layout(height=600, template="plotly_dark")
    return fig


# ─── 5. Top 20 Artistas (Ranking) ──────────────────────────────────────────

def create_top_artists_ranking(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Ranking horizontal dos artistas."""
    top_artists = (
        df.groupby("artist")["minutes_played"]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values("minutes_played")
    )

    fig = px.bar(
        top_artists,
        x="minutes_played",
        y="artist",
        color="minutes_played",
        color_continuous_scale="Greens",
        title=f"Top {top_n} Artistas (Minutos Ouvidos)",
        labels={"minutes_played": "Minutos", "artist": "Artista"},
        orientation="h",
        template="plotly_dark",
        text="minutes_played",
    )

    fig.update_layout(
        height=max(400, len(top_artists) * 35),
        yaxis={"categoryorder": "total ascending"},
        hovermode="y unified",
        coloraxis_showscale=False,
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} min<extra></extra>",
    )

    return fig


# ─── 6. Evolução Mensal ────────────────────────────────────────────────────

def create_monthly_evolution(df: pd.DataFrame) -> go.Figure:
    """Evolução de minutos ouvidos ao longo dos meses."""
    monthly = (
        df.groupby([df["ts"].dt.to_period("M")])["minutes_played"]
        .sum()
        .reset_index()
    )
    monthly["ts"] = monthly["ts"].astype(str)

    fig = px.line(
        monthly,
        x="ts",
        y="minutes_played",
        markers=True,
        title="Evolução Mensal de Minutos Ouvidos",
        labels={"ts": "Mês", "minutes_played": "Minutos"},
        template="plotly_dark",
    )

    fig.update_layout(
        height=400,
        hovermode="x unified",
        xaxis=dict(tickangle=-45),
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<extra></extra>",
    )

    return fig


# ─── 7. Rede de Artistas com PyVis ────────────────────────────────────────

def create_artist_network(df: pd.DataFrame, top_n: int = 30) -> str:
    """
    Cria rede de artistas baseada em co-ocorrência dentro de sessões de escuta.

    Dois artistas são conectados quando aparecem na mesma sessão (faixas tocadas
    com intervalo inferior a 30 minutos). Retorna HTML.
    """
    try:
        import networkx as nx
        from pyvis.network import Network
    except ImportError:
        st.error("PyVis não está instalado. Execute: pip install pyvis networkx")
        return None

    # Top artistas por minutos ouvidos
    minutes_by_artist = df.groupby("artist")["minutes_played"].sum()
    top_artists = minutes_by_artist.nlargest(top_n).index.tolist()

    # Filtrar e RESETAR índice (crítico para que diff() funcione corretamente)
    df_top = df[df["artist"].isin(top_artists)].sort_values("ts").reset_index(drop=True).copy()

    if df_top.empty or len(top_artists) < 2:
        st.info("Dados insuficientes para construir a rede de artistas.")
        return None

    # Calcular gaps entre faixas DEPOIS de resetar o índice
    gaps_seconds = df_top["ts"].diff().dt.total_seconds().fillna(0).values

    # Definir sessões: nova sessão quando gap > 30 min
    session_breaks = gaps_seconds > (30 * 60)
    session_ids = session_breaks.cumsum()
    df_top["session_id"] = session_ids

    # Contar co-ocorrências entre pares de artistas dentro de cada sessão
    from itertools import combinations
    from collections import Counter

    pair_counts: Counter = Counter()
    for sid, session_group in df_top.groupby("session_id"):
        artists_in_session = sorted(session_group["artist"].unique())
        if len(artists_in_session) > 1:
            for a1, a2 in combinations(artists_in_session, 2):
                pair_counts[(a1, a2)] += 1

    if not pair_counts:
        st.info("Não há co-ocorrências entre os artistas selecionados (cada um em sua própria sessão).")
        return None

    # Manter apenas as conexões mais fortes (top-K)
    max_edges = max(top_n * 2, 15)
    strongest = sorted(pair_counts.items(), key=lambda kv: kv[1], reverse=True)
    selected = strongest[:max_edges]

    G = nx.Graph()
    for artist in top_artists:
        G.add_node(artist)

    for (a1, a2), w in selected:
        G.add_edge(a1, a2, weight=w)

    # Escalas para tamanho dos nós
    max_minutes = float(minutes_by_artist.loc[top_artists].max()) or 1.0
    max_weight = max(pair_counts.values()) if pair_counts else 1

    net = Network(
        height="650px",
        width="100%",
        directed=False,
        notebook=False,
        bgcolor=COLORS["background"],
        font_color=COLORS["text"],
    )

    net.from_nx(G)

    # Layout com física estável e nós mais espalhados
    net.barnes_hut(
        gravity=-12000,
        central_gravity=0.3,
        spring_length=180,
        spring_strength=0.04,
        damping=0.9,
    )

    # Customizar nós: tamanho proporcional aos minutos, rótulo sempre visível
    for node in net.nodes:
        artist_minutes = float(minutes_by_artist.get(node["id"], 0))
        node["size"] = 12 + (artist_minutes / max_minutes) * 38  # 12 a 50
        node["color"] = COLORS["primary"]
        node["label"] = node["id"]
        node["title"] = f"{node['id']}<br>{artist_minutes:,.0f} min ouvidos"
        node["font"] = {"size": 16, "color": COLORS["text"], "strokeWidth": 3, "strokeColor": COLORS["background"]}

    # Customizar arestas: espessura/opacidade proporcionais à força da conexão
    for edge in net.edges:
        w = edge.get("weight", 1)
        ratio = w / max_weight
        edge["width"] = 1 + ratio * 6
        opacity = 0.15 + ratio * 0.55
        edge["color"] = {"color": COLORS["primary"], "opacity": round(opacity, 2)}
        edge["title"] = f"{w} sessões juntas"

    # Gerar o HTML em memória (mais robusto que net.show).
    try:
        html = net.generate_html(notebook=False)
    except TypeError:
        html = net.generate_html()
    except Exception:
        import tempfile, os
        tmp_path = os.path.join(tempfile.gettempdir(), "artist_network.html")
        net.write_html(tmp_path, notebook=False, open_browser=False)
        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()

    return html


# ─── 8. Bar Chart Race dos Artistas ────────────────────────────────────────

def create_bar_chart_race(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Bar Chart Race: evolução acumulada dos artistas mês a mês."""
    # Preparar dados mensais por artista
    monthly_artist = (
        df.groupby([df["ts"].dt.to_period("M"), "artist"])["minutes_played"]
        .sum()
        .reset_index()
    )
    monthly_artist["ts"] = monthly_artist["ts"].astype(str)
    monthly_artist = monthly_artist.sort_values("ts")

    # Calcular acumulado
    monthly_artist["cumulative"] = monthly_artist.groupby("artist")["minutes_played"].cumsum()

    # Top artistas globais
    top_artists = (
        df.groupby("artist")["minutes_played"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )

    monthly_artist = monthly_artist[monthly_artist["artist"].isin(top_artists)]

    # Garantir que todos os artistas aparecem em todos os meses (com 0 se necessário)
    all_months = sorted(monthly_artist["ts"].unique())
    all_combinations = pd.MultiIndex.from_product(
        [all_months, top_artists], names=["ts", "artist"]
    ).to_frame(index=False)

    monthly_artist = all_combinations.merge(
        monthly_artist, on=["ts", "artist"], how="left"
    ).fillna(0)

    monthly_artist["cumulative"] = monthly_artist.groupby("artist")["cumulative"].transform(
        lambda x: x.ffill().fillna(0)
    )

    # Criar animação
    fig = px.bar(
        monthly_artist,
        x="cumulative",
        y="artist",
        animation_frame="ts",
        animation_group="artist",
        orientation="h",
        color="artist",
        title=f"Bar Chart Race: Top {top_n} Artistas",
        labels={"cumulative": "Minutos Acumulados", "artist": "Artista"},
        template="plotly_dark",
    )

    fig.update_layout(
        height=500,
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        hovermode="y unified",
    )

    return fig
