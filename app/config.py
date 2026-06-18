"""Configuração centralizada do Spotify Rewind App."""

import streamlit as st

# ─── Page Config ───────────────────────────────────────────────────────────
PAGE_CONFIG = {
    "page_title": "Spotify Rewind",
    "page_icon": "🎵",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ─── Cores (inspiradas no tema Spotify) ────────────────────────────────────
COLORS = {
    "primary": "#1DB954",        # verde Spotify
    "background": "#191414",     # fundo escuro
    "secondary_bg": "#282828",   # cards / sidebar
    "text": "#FFFFFF",
    "muted": "#b3b3b3",
    "accent": "#1ed760",
    "error": "#e74c3c",
    "warning": "#f39c12",
}

# ─── Labels / Constantes ───────────────────────────────────────────────────
MONTH_LABELS = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]

MONTH_NUM_TO_LABEL = {i + 1: label for i, label in enumerate(MONTH_LABELS)}

DAY_LABELS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

PLATFORM_CATEGORIES = {
    "android": "Android",
    "ios": "iOS",
    "windows": "Windows",
    "mac": "macOS",
    "web": "Web Player",
    "tv": "TV",
    "chromecast": "Chromecast",
    "car": "Carro",
    "watch": "Relógio",
    "other": "Outro",
}

# ─── TABS ───────────────────────────────────────────────────────────────────
TABS = [
    ("📊", "Visão Geral"),
    ("📈", "Tendências"),
    ("🎵", "Músicas"),
    ("👤", "Artistas"),
    ("🔄", "Sessões"),
    ("📱", "Plataforma"),
    ("✨", "Análises Avançadas"),
    ("ℹ️", "Sobre"),
]

DEFAULT_TOP_N = 15

# ─── DEV MODE (pular upload, ler diretório local) ──────────────────────────
# DEV_MODE=True carrega dados locais automaticamente (apenas para desenvolvimento).
# DEV_MODE=False habilita o upload do ZIP pelo próprio usuário (modo de produção).
DEV_MODE = False
DEV_DATA_PATH = r"C:\Users\eferro\Desktop\Spotify-Rewind\my_spotify_data\Spotify Extended Streaming History"


# ─── Injetar CSS customizado ───────────────────────────────────────────────
def inject_custom_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLORS["background"]};
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 4px 4px 0 0;
            padding: 10px 16px;
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COLORS["secondary_bg"]} !important;
        }}
        .metric-card {{
            background-color: {COLORS["secondary_bg"]};
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid #333;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 800;
            color: {COLORS["primary"]};
            line-height: 1.2;
        }}
        .metric-label {{
            font-size: 13px;
            color: {COLORS["muted"]};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }}
        .header-title {{
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["accent"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0;
        }}
        .header-subtitle {{
            color: {COLORS["muted"]};
            text-align: center;
            font-size: 1rem;
            margin-top: 2px;
        }}
        .footer {{
            text-align: center;
            color: {COLORS["muted"]};
            font-size: 12px;
            padding: 20px 0;
        }}
        .stChat {{
            background-color: {COLORS["secondary_bg"]};
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLORS["primary"]} !important;
            font-weight: 800 !important;
        }}
        div[data-testid="stMetricDelta"] {{
            color: {COLORS["muted"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
