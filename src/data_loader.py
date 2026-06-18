"""
Módulo de carregamento de dados do Spotify Rewind.
Gerencia upload ZIP, parse de múltiplos JSONs, limpeza e feature engineering.
"""

import io
import json
import zipfile
import os

import pandas as pd
import streamlit as st


def _parse_platform(platform_raw: str) -> str:
    """Normaliza string de plataforma para categoria legível."""
    if not isinstance(platform_raw, str):
        return "Outro"
    p = platform_raw.lower()
    if "android" in p:
        return "Android"
    if "ios" in p or "iphone" in p or "ipad" in p:
        return "iOS"
    if "windows" in p:
        return "Windows"
    if "mac" in p:
        return "macOS"
    if "web" in p or "browser" in p:
        return "Web Player"
    if "tv" in p or "tizen" in p or "webos" in p:
        return "TV"
    if "chromecast" in p or "cast" in p:
        return "Chromecast"
    if "car" in p or "vehicle" in p:
        return "Carro"
    if "watch" in p:
        return "Relógio"
    return "Outro"


@st.cache_data(show_spinner="🔄 Carregando dados do Spotify...")
def load_data_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    """
    Carrega dados de um ZIP baixado via upload (Streamlit file_uploader).
    Retorna DataFrame completo com feature engineering aplicada.
    """
    return _parse_zip(file_bytes)


@st.cache_data(show_spinner="🔄 Carregando dados locais...")
def load_data_from_directory(directory: str) -> pd.DataFrame:
    """
    Carrega dados a partir de um diretório local com JSONs.
    Usado em DEV_MODE.
    """
    dfs = []
    json_files = sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".json")
    ])

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        df_part = pd.DataFrame(data)
        if not df_part.empty:
            dfs.append(df_part)

    df = pd.concat(dfs, ignore_index=True)
    return _apply_feature_engineering(df)


def _parse_zip(file_bytes: bytes) -> pd.DataFrame:
    """
    Extrai JSONs do ZIP, carrega cada um como DataFrame,
    concatena e aplica feature engineering.

    Suporta os dois formatos de exportação do Spotify:
    - Extended Streaming History (Streaming_History_Audio_*.json)
    - Account Data / StreamingHistory*.json (formato simplificado)
    """
    dfs = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        all_names = z.namelist()

        # 1ª prioridade: Extended Streaming History (formato completo)
        json_files = sorted([
            f for f in all_names
            if f.endswith(".json")
            and ("Streaming_History" in f or "streaming_history" in f.lower())
        ])

        # 2ª prioridade: Account Data (StreamingHistory*.json - formato simplificado)
        if not json_files:
            json_files = sorted([
                f for f in all_names
                if f.endswith(".json") and "streaminghistory" in f.lower().replace("_", "")
            ])

        # Fallback: qualquer JSON que pareça conter histórico de reprodução
        if not json_files:
            json_files = sorted([
                f for f in all_names
                if f.endswith(".json") and "history" in f.lower()
            ])

        if not json_files:
            raise ValueError(
                "Nenhum arquivo de histórico de reprodução encontrado no ZIP. "
                "Certifique-se de enviar o ZIP do 'Spotify Extended Streaming History' "
                "ou do 'Account Data', que contém arquivos como "
                "'Streaming_History_Audio_*.json' ou 'StreamingHistory*.json'."
            )

        for jf in json_files:
            with z.open(jf) as f:
                raw = f.read().decode("utf-8")
                data = json.loads(raw)
            df_part = pd.DataFrame(data)
            if not df_part.empty:
                dfs.append(df_part)

    if not dfs:
        raise ValueError("Os arquivos JSON encontrados no ZIP estão vazios.")

    df = pd.concat(dfs, ignore_index=True)
    df = _normalize_account_data_format(df)
    return _apply_feature_engineering(df)


def _normalize_account_data_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o formato simplificado (Account Data) para o formato
    do Extended Streaming History, garantindo as colunas esperadas.
    """
    # Formato simplificado usa endTime / msPlayed / artistName / trackName
    rename_map = {}
    if "endTime" in df.columns and "ts" not in df.columns:
        rename_map["endTime"] = "ts"
    if "msPlayed" in df.columns and "ms_played" not in df.columns:
        rename_map["msPlayed"] = "ms_played"
    if "artistName" in df.columns and "master_metadata_album_artist_name" not in df.columns:
        rename_map["artistName"] = "master_metadata_album_artist_name"
    if "trackName" in df.columns and "master_metadata_track_name" not in df.columns:
        rename_map["trackName"] = "master_metadata_track_name"

    if rename_map:
        df = df.rename(columns=rename_map)

    return df


def _apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformações e colunas derivadas no DataFrame bruto."""

    # Timestamp → datetime
    df["ts"] = pd.to_datetime(df["ts"], utc=True)

    # Ordenar por timestamp
    df = df.sort_values("ts").reset_index(drop=True)

    # ms_played → minutos
    df["minutes_played"] = df["ms_played"] / 60000.0

    # Colunas temporais derivadas
    df["year"] = df["ts"].dt.year.astype(int)
    df["month"] = df["ts"].dt.month.astype(int)
    df["month_name"] = df["ts"].dt.month_name()
    df["hour"] = df["ts"].dt.hour.astype(int)
    df["day_of_week"] = df["ts"].dt.day_name()
    df["date"] = df["ts"].dt.date

    # Normalizar plataforma
    if "platform" in df.columns:
        df["platform_category"] = df["platform"].apply(_parse_platform)
    else:
        df["platform_category"] = "Desconhecida"

    # Normalizar nomes de colunas de artista/álbum/música
    df.rename(
        columns={
            "master_metadata_album_artist_name": "artist",
            "master_metadata_track_name": "track_name",
            "master_metadata_album_album_name": "album_name",
        },
        inplace=True,
    )

    # Remover streams sem metadados (ex: podcasts, episódios sem nome)
    df = df[df["track_name"].notna()].copy()
    df["artist"] = df["artist"].fillna("Artista Desconhecido")
    df["album_name"] = df["album_name"].fillna("Álbum Desconhecido")

    # Remover registros com ms_played muito pequeno (skips / erros)
    df = df[df["ms_played"] >= 5000].copy()

    # Flag para dados de vídeo vs. áudio
    df["is_video"] = df.get("episode_show_name", pd.Series([None] * len(df))).notna()

    return df.reset_index(drop=True)
