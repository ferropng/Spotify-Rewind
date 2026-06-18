"""
Módulo de gráficos do Spotify Rewind.
Cada função retorna uma Figure Plotly pronta para st.plotly_chart().
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.config import COLORS, DAY_ORDER, DAY_LABELS, MONTH_LABELS, MONTH_NUM_TO_LABEL


def _dark_template():
    """Template escuro customizado."""
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=COLORS["background"],
            plot_bgcolor=COLORS["secondary_bg"],
            font=dict(color=COLORS["text"], family="Arial, sans-serif"),
            xaxis=dict(
                gridcolor="#333",
                zerolinecolor="#444",
                tickfont=dict(color=COLORS["muted"]),
            ),
            yaxis=dict(
                gridcolor="#333",
                zerolinecolor="#444",
                tickfont=dict(color=COLORS["muted"]),
            ),
            hoverlabel=dict(
                bgcolor=COLORS["secondary_bg"],
                font_color=COLORS["text"],
            ),
            legend=dict(
                font=dict(color=COLORS["muted"]),
            ),
        )
    )


# ─── Visão Geral ────────────────────────────────────────────────────────────

def create_yearly_bar(yearly_df: pd.DataFrame) -> go.Figure:
    """Minutos ouvidos por ano — barras com gradiente."""
    fig = px.bar(
        yearly_df,
        x="year",
        y="Minutos",
        title="Minutos Ouvidos por Ano",
        labels={"Minutos": "Minutos", "year": "Ano"},
        color="Minutos",
        color_continuous_scale="Greens",
        template="plotly_dark",
    )
    fig.update_layout(
        height=400,
        hovermode="x unified",
        xaxis=dict(dtick=1),
        coloraxis_showscale=False,
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<extra></extra>",
        marker_line_width=0,
    )
    return fig


def create_monthly_comparison_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """Comparação mensal entre anos — barras agrupadas."""
    fig = px.bar(
        monthly_df,
        x="month_name",
        y="minutes_played",
        color="year",
        title="Comparação Mensal de Minutos Ouvidos",
        labels={"minutes_played": "Minutos", "month_name": "Mês", "year": "Ano"},
        template="plotly_dark",
        color_continuous_scale="Greens",
        barmode="group",
    )
    fig.update_layout(
        height=450,
        hovermode="x unified",
        xaxis_title="Mês",
        yaxis_title="Minutos Ouvidos",
        coloraxis_showscale=False,
    )
    # Renomear meses para pt-br
    month_map = {
        "January": "Jan", "February": "Fev", "March": "Mar",
        "April": "Abr", "May": "Mai", "June": "Jun",
        "July": "Jul", "August": "Ago", "September": "Set",
        "October": "Out", "November": "Nov", "December": "Dez",
    }
    fig.update_xaxes(tickvals=list(month_map.keys()), ticktext=list(month_map.values()))
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<br>Ano: %{marker.color}<extra></extra>")
    return fig


# ─── Padrões de Escuta ──────────────────────────────────────────────────────

def create_hourly_chart(hourly_df: pd.DataFrame) -> go.Figure:
    """Distribuição por hora do dia — área."""
    fig = px.area(
        hourly_df,
        x="hour",
        y="Minutos",
        title="Distribuição de Escuta por Hora do Dia",
        labels={"Minutos": "Minutos Ouvidos", "hour": "Hora do Dia"},
        template="plotly_dark",
    )
    fig.update_layout(
        height=400,
        hovermode="x unified",
        xaxis=dict(dtick=1, range=[0, 23]),
    )
    fig.update_traces(
        line=dict(color=COLORS["primary"], width=2),
        fillcolor="rgba(29, 185, 84, 0.15)",
        hovertemplate="<b>%{x}h</b><br>%{y:,.0f} min<extra></extra>",
    )
    # Destacar pico
    peak = hourly_df.loc[hourly_df["Minutos"].idxmax()]
    fig.add_annotation(
        x=peak["hour"],
        y=peak["Minutos"],
        text=f"🔺 Pico: {int(peak['hour'])}h",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLORS["accent"],
        font=dict(color=COLORS["accent"], size=12),
    )
    return fig


def create_weekly_chart(weekly_df: pd.DataFrame) -> go.Figure:
    """Distribuição por dia da semana — barras."""
    day_map = dict(zip(DAY_ORDER, DAY_LABELS))
    weekly_df = weekly_df.copy()
    weekly_df["day_label"] = weekly_df["day_of_week"].map(day_map)

    fig = px.bar(
        weekly_df,
        x="day_label",
        y="Minutos",
        title="Distribuição de Escuta por Dia da Semana",
        labels={"Minutos": "Minutos Ouvidos", "day_label": "Dia da Semana"},
        color="Minutos",
        color_continuous_scale="Greens",
        template="plotly_dark",
    )
    fig.update_layout(
        height=400,
        hovermode="x unified",
        coloraxis_showscale=False,
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<extra></extra>"
    )
    return fig


def create_heatmap(heatmap_df: pd.DataFrame) -> go.Figure:
    """Heatmap: dia da semana × hora."""
    day_map = dict(zip(DAY_ORDER, DAY_LABELS))
    heatmap_df = heatmap_df.copy()
    heatmap_df.index = heatmap_df.index.map(day_map)

    fig = px.imshow(
        heatmap_df,
        labels=dict(x="Hora do Dia", y="Dia da Semana", color="Minutos"),
        title="Padrão de Escuta por Hora e Dia da Semana",
        color_continuous_scale="Greens",
        aspect="auto",
        template="plotly_dark",
    )
    fig.update_layout(
        height=420,
        xaxis=dict(dtick=1),
    )
    fig.update_traces(hovertemplate="<b>%{y}</b> | <b>%{x}h</b><br>%{z:,.0f} min<extra></extra>")
    return fig


# ─── Músicas ────────────────────────────────────────────────────────────────

def create_top_tracks_chart(top_df: pd.DataFrame, metric: str = "plays") -> go.Figure:
    """Top N músicas — barras horizontais."""
    value_col = "Vezes tocada" if metric == "plays" else "Minutos"
    fig = px.bar(
        top_df,
        x=value_col,
        y="Música",
        color=value_col,
        color_continuous_scale="Greens",
        title=f"Top {len(top_df)} {value_col}",
        labels={value_col: value_col, "Música": "Música"},
        orientation="h",
        template="plotly_dark",
        text=value_col,
    )
    fig.update_layout(
        height=max(400, len(top_df) * 35),
        yaxis={"categoryorder": "total ascending"},
        hovermode="y unified",
        coloraxis_showscale=False,
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    )
    return fig


def create_top_tracks_by_artist_chart(top_df: pd.DataFrame) -> go.Figure:
    """Top N músicas com destaque por artista. Detecta a métrica automaticamente."""
    # Detecta qual métrica está presente no DataFrame
    if "Vezes tocada" in top_df.columns:
        value_col = "Vezes tocada"
        title = f"Top {len(top_df)} Músicas Mais Tocadas"
        hover_template = "<b>%{y}</b><br>Plays: %{x:,.0f}<br>Artista: %{marker.color}<extra></extra>"
    elif "Minutos" in top_df.columns:
        value_col = "Minutos"
        title = f"Top {len(top_df)} Músicas (minutos ouvidos)"
        hover_template = "<b>%{y}</b><br>%{x:,.0f} minutos<br>Artista: %{marker.color}<extra></extra>"
    else:
        numeric_cols = [c for c in top_df.columns if c not in ("Música", "Artista")]
        value_col = numeric_cols[0] if numeric_cols else top_df.columns[-1]
        title = f"Top {len(top_df)} Músicas"
        hover_template = "<b>%{y}</b><br>%{x:,.0f}<br>Artista: %{marker.color}<extra></extra>"

    fig = px.bar(
        top_df,
        x=value_col,
        y="Música",
        color="Artista",
        title=title,
        orientation="h",
        template="plotly_dark",
    )
    fig.update_layout(
        height=max(400, len(top_df) * 35),
        yaxis={"categoryorder": "total ascending"},
        hovermode="y unified",
    )
    fig.update_traces(
        hovertemplate=hover_template,
    )
    return fig


# ─── Artistas ───────────────────────────────────────────────────────────────

def create_top_artists_chart(top_df: pd.DataFrame) -> go.Figure:
    """Top N artistas — barras horizontais. Detecta a métrica automaticamente."""
    # Detecta qual métrica está presente no DataFrame
    if "Horas" in top_df.columns:
        value_col = "Horas"
        title = f"Top {len(top_df)} Artistas (horas ouvidas)"
        text_template = "%{text:,.1f}h"
        hover_template = "<b>%{y}</b><br>%{x:,.1f} horas<extra></extra>"
    elif "Vezes tocada" in top_df.columns:
        value_col = "Vezes tocada"
        title = f"Top {len(top_df)} Artistas (vezes tocadas)"
        text_template = "%{text:,.0f}"
        hover_template = "<b>%{y}</b><br>%{x:,.0f} plays<extra></extra>"
    elif "Minutos" in top_df.columns:
        value_col = "Minutos"
        title = f"Top {len(top_df)} Artistas (minutos ouvidos)"
        text_template = "%{text:,.0f}"
        hover_template = "<b>%{y}</b><br>%{x:,.0f} minutos<extra></extra>"
    else:
        # Fallback: usa a primeira coluna numérica disponível
        numeric_cols = [c for c in top_df.columns if c != "Artista"]
        value_col = numeric_cols[0] if numeric_cols else top_df.columns[-1]
        title = f"Top {len(top_df)} Artistas"
        text_template = "%{text:,.0f}"
        hover_template = "<b>%{y}</b><br>%{x:,.0f}<extra></extra>"

    fig = px.bar(
        top_df,
        x=value_col,
        y="Artista",
        color=value_col,
        color_continuous_scale="Greens",
        title=title,
        labels={value_col: value_col, "Artista": "Artista"},
        orientation="h",
        template="plotly_dark",
        text=value_col,
    )
    fig.update_layout(
        height=max(400, len(top_df) * 35),
        yaxis={"categoryorder": "total ascending"},
        hovermode="y unified",
        coloraxis_showscale=False,
    )
    fig.update_traces(
        texttemplate=text_template,
        textposition="outside",
        hovertemplate=hover_template,
    )
    return fig


def create_artist_evolution_chart(evolution_df: pd.DataFrame) -> go.Figure:
    """Evolução anual dos top artistas — linhas."""
    fig = px.line(
        evolution_df,
        x="year",
        y="minutes_played",
        color="artist",
        title="Evolução dos Artistas Mais Ouvidos",
        labels={
            "minutes_played": "Minutos Ouvidos",
            "year": "Ano",
            "artist": "Artista",
        },
        markers=True,
        template="plotly_dark",
    )
    fig.update_layout(
        height=500,
        hovermode="x unified",
        xaxis=dict(dtick=1),
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=8),
        hovertemplate="<b>%{fullData.name}</b><br>Ano: %{x}<br>%{y:,.0f} min<extra></extra>",
    )
    return fig


# ─── Sessões ────────────────────────────────────────────────────────────────

def create_session_histogram(sessions_df: pd.DataFrame) -> go.Figure:
    """Distribuição da duração das sessões."""
    fig = px.histogram(
        sessions_df,
        x="session_duration",
        title="Distribuição da Duração das Sessões de Escuta",
        labels={"session_duration": "Duração da Sessão (minutos)", "count": "Quantidade"},
        nbins=200,
        template="plotly_dark",
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_layout(
        height=450,
        bargap=0.05,
        hovermode="x",
        xaxis=dict(range=[0, min(500, sessions_df["session_duration"].max())]),
    )
    fig.update_traces(
        hovertemplate="<b>%{x:.0f} min</b><br>%{y} sessões<extra></extra>"
    )

    # Média
    mean_dur = sessions_df["session_duration"].mean()
    fig.add_vline(
        x=mean_dur,
        line_dash="dash",
        line_color=COLORS["accent"],
        annotation_text=f"Média: {mean_dur:.0f} min",
        annotation_font_color=COLORS["accent"],
    )
    return fig


# ─── Plataforma ─────────────────────────────────────────────────────────────

def create_platform_pie(platform_series: pd.Series) -> go.Figure:
    """Distribuição por plataforma — pizza."""
    fig = px.pie(
        values=platform_series.values,
        names=platform_series.index,
        title="Minutos por Plataforma",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} min<br>%{percent}<extra></extra>",
    )
    fig.update_layout(height=450)
    return fig


def create_platform_trends_chart(trends_df: pd.DataFrame) -> go.Figure:
    """Evolução do uso de plataformas por ano."""
    fig = px.area(
        trends_df,
        x="year",
        y="minutes_played",
        color="platform_category",
        title="Evolução do Uso por Plataforma",
        labels={
            "minutes_played": "Minutos",
            "year": "Ano",
            "platform_category": "Plataforma",
        },
        template="plotly_dark",
        groupnorm=None,
    )
    fig.update_layout(
        height=450,
        hovermode="x unified",
        xaxis=dict(dtick=1),
    )
    return fig


# ─── Métricas como Sparklines ───────────────────────────────────────────────

def create_mini_sparkline(data: pd.Series, color: str = COLORS["primary"]) -> go.Figure:
    """Mini gráfico sparkline para exibição inline."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=data.values,
            mode="lines",
            line=dict(color=color, width=2),
            showlegend=False,
        )
    )
    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        hovermode=False,
    )
    return fig


# ─── Tabela Estilizada ──────────────────────────────────────────────────────

def create_styled_table(df: pd.DataFrame, title: str = "") -> go.Figure:
    """Tabela estilo Spotify com tema escuro."""
    header_color = COLORS["secondary_bg"]
    cell_color = COLORS["background"]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color=header_color,
                    font=dict(color=COLORS["primary"], size=13, family="Arial"),
                    align="left",
                    height=36,
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color=cell_color,
                    font=dict(color=COLORS["text"], size=12),
                    align="left",
                    height=30,
                    format=[",.0f" if df[col].dtype in ("int64", "float64") else None for col in df.columns],
                ),
            )
        ]
    )
    fig.update_layout(
        title=title,
        height=40 + len(df) * 32,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig
