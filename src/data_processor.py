"""
Módulo de processamento e filtragem de dados do Spotify Rewind.
Funções puras que recebem DataFrame e retornam resultados agregados.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple


# ─── Filtros ────────────────────────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    years: Optional[List[int]] = None,
    artists: Optional[List[str]] = None,
    search_query: str = "",
) -> pd.DataFrame:
    """
    Aplica filtros combinados no DataFrame.
    """
    filtered = df.copy()

    if years:
        filtered = filtered[filtered["year"].isin(years)]

    if artists:
        filtered = filtered[filtered["artist"].isin(artists)]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["track_name"].str.lower().str.contains(q, na=False)
            | filtered["artist"].str.lower().str.contains(q, na=False)
        ]

    return filtered


# ─── Estatísticas Globais ───────────────────────────────────────────────────

def compute_global_stats(df: pd.DataFrame) -> dict:
    """
    Retorna dicionário com métricas agregadas do dataset.
    """
    total_minutes = df["minutes_played"].sum()
    total_hours = total_minutes / 60.0
    total_days = total_hours / 24.0

    unique_dates = df["date"].nunique()
    avg_daily_minutes = total_minutes / unique_dates if unique_dates > 0 else 0

    # Contagens
    total_streams = len(df)
    unique_tracks = df["track_name"].nunique()
    unique_artists = df["artist"].nunique()
    year_range = (df["year"].min(), df["year"].max())

    # Top artista e música (tudo)
    top_artist = (
        df.groupby("artist")["minutes_played"].sum().idxmax()
    )
    top_track_row = (
        df.groupby(["track_name", "artist"])["minutes_played"]
        .sum()
        .idxmax()
    )
    top_track_name = top_track_row[0]
    top_track_artist = top_track_row[1]

    # Picos
    peak_hour = (
        df.groupby("hour")["minutes_played"].sum().idxmax()
    )
    peak_day = (
        df.groupby("day_of_week")["minutes_played"].sum().idxmax()
    )

    return {
        "total_minutes": round(total_minutes),
        "total_hours": round(total_hours, 1),
        "total_days": round(total_days, 1),
        "avg_daily_minutes": round(avg_daily_minutes, 1),
        "total_streams": total_streams,
        "unique_tracks": unique_tracks,
        "unique_artists": unique_artists,
        "year_range": year_range,
        "top_artist": top_artist,
        "top_track_name": top_track_name,
        "top_track_artist": top_track_artist,
        "peak_hour": peak_hour,
        "peak_day": peak_day,
        "first_date": df["date"].min(),
        "last_date": df["date"].max(),
    }


# ─── Top N ──────────────────────────────────────────────────────────────────

def get_top_tracks(df: pd.DataFrame, n: int = 10, metric: str = "plays") -> pd.DataFrame:
    """
    Retorna top N músicas por número de plays ou minutos.
    """
    if metric == "minutes":
        top = (
            df.groupby(["track_name", "artist"])["minutes_played"]
            .sum()
            .nlargest(n)
            .reset_index()
        )
        top.columns = ["Música", "Artista", "Minutos"]
    else:
        top = (
            df.groupby(["track_name", "artist"])
            .size()
            .nlargest(n)
            .reset_index(name="Plays")
        )
        top.columns = ["Música", "Artista", "Vezes tocada"]

    return top


def get_top_artists(
    df: pd.DataFrame, n: int = 10, metric: str = "minutes"
) -> pd.DataFrame:
    """
    Retorna top N artistas por minutos ouvidos ou plays.
    """
    if metric == "plays":
        top = (
            df["artist"].value_counts().nlargest(n).reset_index()
        )
        top.columns = ["Artista", "Vezes tocada"]
    else:
        top = (
            df.groupby("artist")["minutes_played"]
            .sum()
            .nlargest(n)
            .reset_index()
        )
        top.columns = ["Artista", "Minutos"]
        top["Horas"] = (top["Minutos"] / 60).round(1)

    return top


# ─── Análises Temporais ─────────────────────────────────────────────────────

def get_yearly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Minutos ouvidos por ano."""
    return (
        df.groupby("year")["minutes_played"]
        .sum()
        .reset_index()
        .rename(columns={"minutes_played": "Minutos"})
    )


def get_monthly_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Minutos ouvidos por mês, agrupado por ano."""
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    monthly = (
        df.groupby(["year", "month_name"])["minutes_played"]
        .sum()
        .reset_index()
    )
    monthly["month_name"] = pd.Categorical(
        monthly["month_name"], categories=month_order, ordered=True
    )
    return monthly.sort_values(["year", "month_name"])


def get_hourly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Minutos ouvidos por hora do dia."""
    return (
        df.groupby("hour")["minutes_played"]
        .sum()
        .reset_index()
        .rename(columns={"minutes_played": "Minutos"})
    )


def get_weekly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Minutos ouvidos por dia da semana."""
    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday",
    ]
    dist = (
        df.groupby("day_of_week")["minutes_played"]
        .sum()
        .reindex(day_order)
        .reset_index()
        .rename(columns={"minutes_played": "Minutos"})
    )
    return dist


def get_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: dia da semana × hora do dia, preenchido com 0."""
    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday",
    ]
    return (
        df.pivot_table(
            index="day_of_week",
            columns="hour",
            values="minutes_played",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(day_order)
    )


def get_artist_evolution(
    df: pd.DataFrame, top_n: int = 10
) -> pd.DataFrame:
    """
    Evolução anual dos top N artistas (em minutos).
    """
    top_artists = (
        df.groupby("artist")["minutes_played"]
        .sum()
        .nlargest(top_n)
        .index
    )
    evolution = (
        df[df["artist"].isin(top_artists)]
        .groupby(["year", "artist"])["minutes_played"]
        .sum()
        .reset_index()
    )
    return evolution


# ─── Sessões ────────────────────────────────────────────────────────────────

def get_session_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica sessões de escuta (gap ≥ 30 min = nova sessão)
    e retorna DataFrame com duração e tracks por sessão.
    """
    df_sorted = df.sort_values("ts").copy()
    time_diff = df_sorted["ts"].diff().dt.total_seconds() / 60.0
    df_sorted["session_id"] = (time_diff > 30).cumsum()

    sessions = (
        df_sorted.groupby("session_id")
        .agg(
            start_time=("ts", "min"),
            end_time=("ts", "max"),
            total_minutes=("minutes_played", "sum"),
            tracks_played=("track_name", "count"),
        )
        .reset_index()
    )

    sessions["session_duration"] = (
        sessions["end_time"] - sessions["start_time"]
    ).dt.total_seconds() / 60.0

    # Ignorar sessões muito curtas (< 10 min)
    sessions = sessions[sessions["session_duration"] >= 10].reset_index(drop=True)
    return sessions


# ─── Plataforma ─────────────────────────────────────────────────────────────

def get_platform_distribution(df: pd.DataFrame) -> pd.Series:
    """Distribuição de minutos ouvidos por categoria de plataforma."""
    return df.groupby("platform_category")["minutes_played"].sum().sort_values(ascending=False)


def get_platform_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Evolução anual do uso de plataformas."""
    return (
        df.groupby(["year", "platform_category"])["minutes_played"]
        .sum()
        .reset_index()
    )


def get_country_distribution(df: pd.DataFrame) -> pd.Series:
    """Distribuição por país de conexão (conn_country)."""
    if "conn_country" not in df.columns:
        return pd.Series(dtype=float)
    return df.groupby("conn_country")["minutes_played"].sum().sort_values(ascending=False)
