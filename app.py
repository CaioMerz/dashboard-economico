import html
import re
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st
from typing import Any

try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    go = None

from utils.kpis import carregar_kpis_home


st.set_page_config(
    page_title="Dashboard Economico",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --brand-primary: #1f3b5c;
        --brand-secondary: #6b7280;
        --brand-accent: #2f855a;
        --page-bg: #eef1f5;
        --card-surface: #ffffff;
        --card-border: #d9e0e7;
        --text-main: #1f2937;
        --text-muted: #6b7280;
    }

    .stApp {
        background-color: var(--page-bg);
        color: var(--text-main);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.9rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    section.main > div {
        gap: 0.95rem;
    }

    h1, h2, h3 {
        color: var(--brand-primary);
        letter-spacing: -0.4px;
        font-weight: 680;
        margin-bottom: 0.55rem;
    }

    h1 {
        font-size: clamp(2.05rem, 3vw, 2.7rem);
        font-weight: 760;
        line-height: 1.08;
        margin-bottom: 0.2rem;
    }

    a, a:visited {
        color: var(--brand-primary);
        text-decoration-color: rgba(31, 59, 87, 0.35);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--card-surface);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 0.4rem 0.5rem;
        box-shadow: 0 1px 1px rgba(16, 24, 40, 0.02);
        transition: box-shadow 0.15s ease;
        cursor: pointer;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 12px rgba(31, 59, 92, 0.12);
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }

    [data-testid="stSidebar"] {
        background: #f1f4f7;
        border-right: 1px solid #e0e6ed;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        color: #334155;
        margin: 0.08rem 0;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: #e7edf3;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #e1e8f0;
        color: var(--brand-primary);
        font-weight: 600;
        border-left: 2px solid var(--brand-primary);
    }

    .home-subtitle {
        margin: 0.18rem 0 0 0;
        color: #4f5d70;
        font-size: 1.1rem;
        font-weight: 560;
        line-height: 1.32;
    }

    .home-support {
        margin: 0.42rem 0 0 0;
        color: #6a7381;
        font-size: 0.95rem;
        line-height: 1.38;
    }

    .kpi-analitico {
        min-height: 220px;
        height: 100%;
        border: 1px solid #e0e0e0;
        border-top: 3px solid #1f3b5c;
        border-radius: 10px;
        background: #ffffff;
        padding: 20px 20px 14px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
    }

    .kpi-analitico-label {
        margin: 0;
        font-size: 0.72rem;
        color: #8b95a5;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
    }

    .kpi-analitico-valor {
        margin: 0.3rem 0 0.22rem 0;
        font-size: 2.46rem;
        font-weight: 780;
        line-height: 1.01;
        letter-spacing: -0.02em;
    }

    .kpi-analitico-comparacao {
        margin: 0.02rem 0 0 0;
        font-size: 0.88rem;
        font-weight: 620;
        line-height: 1.28;
        color: #334155;
    }

    .kpi-analitico-comparacao-destaque {
        font-weight: 700;
        color: #1f3b5c;
    }

    .kpi-analitico-apoios {
        margin-top: 0.34rem;
    }

    .kpi-analitico-apoio {
        margin: 0.09rem 0 0 0;
        font-size: 0.78rem;
        color: #4b5565;
        line-height: 1.24;
    }

    .kpi-analitico-apoio-forte {
        color: #334155;
        font-weight: 620;
    }

    .kpi-analitico-apoio-neutro {
        color: #556274;
        font-weight: 500;
    }

    .kpi-analitico-apoio-suave {
        color: #6b7280;
        font-weight: 500;
    }

    .kpi-analitico-interpretacao {
        margin: 0.5rem 0 0 0;
        font-size: 0.74rem;
        color: #6d7786;
        font-style: italic;
        line-height: 1.27;
    }

    .kpi-analitico-secundario {
        margin: 0.42rem 0 0 0;
        font-size: 0.61rem;
        color: #b3bcc8;
        font-weight: 430;
        line-height: 1.22;
    }

    .kpi-spark-separador {
        border-top: 1px solid #e9edf3;
        margin: 0.34rem 0 0.18rem 0;
    }

    .portfolio-title {
        margin: 0;
        color: var(--brand-primary);
        font-weight: 700;
        font-size: 1rem;
    }

    .portfolio-text {
        margin: 0.4rem 0 0.8rem 0;
        color: #334155;
        font-size: 0.9rem;
        line-height: 1.3;
        min-height: 3.8rem;
    }

    .home-footer {
        margin-top: 0.55rem;
        text-align: center;
        color: #8f99a8;
        font-size: 0.74rem;
        line-height: 1.4;
    }

    .home-footer a {
        color: #708096;
        text-decoration: none;
        margin: 0 0.22rem;
    }

    .home-footer a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _normalizar_coluna(texto: str) -> str:
    texto_limpo = str(texto or "").strip().lower()
    return unicodedata.normalize("NFKD", texto_limpo).encode("ascii", "ignore").decode("ascii")


def _detectar_coluna(colunas, chaves, excluir=None):
    excluidas = {item for item in (excluir or set()) if item}
    candidatas = [col for col in colunas if col not in excluidas]
    for chave in chaves:
        chave_norm = _normalizar_coluna(chave)
        for coluna in candidatas:
            if chave_norm in _normalizar_coluna(coluna):
                return coluna
    return None


def _valor_percentual_para_float(texto: str | None) -> float | None:
    if not texto:
        return None
    bruto = str(texto).strip().replace("%", "").replace(" ", "")
    bruto = bruto.replace(".", "").replace(",", ".") if "," in bruto else bruto
    try:
        return float(bruto)
    except ValueError:
        return None


def _formatar_percentual_br(valor: float, casas: int = 2, mostrar_sinal: bool = False) -> str:
    sinal = "+" if mostrar_sinal and valor > 0 else ""
    formato = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{formato}%"


def _formatar_pp_br(valor: float, casas: int = 2, mostrar_sinal: bool = True) -> str:
    sinal = "+" if mostrar_sinal and valor >= 0 else ""
    formato = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{formato} p.p."


def _formatar_x_br(valor: float, casas: int = 1) -> str:
    formato = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formato}x"


def _formatar_mes_ano_pt_br(data: pd.Timestamp | None) -> str | None:
    if data is None or pd.isna(data):
        return None
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    return f"{meses[int(data.month) - 1]}/{int(data.year)}"


def _retorno_acumulado_serie(serie: pd.Series) -> float | None:
    serie = pd.to_numeric(serie, errors="coerce").dropna()
    if serie.empty:
        return None
    primeiro = float(serie.iloc[0])
    ultimo = float(serie.iloc[-1])
    if 95 <= primeiro <= 105:
        return ((ultimo / 100) - 1) * 100
    if 0.95 <= primeiro <= 1.05:
        return (ultimo - 1) * 100
    return ultimo


def _renderizar_kpi_analitico(
    coluna,
    label: str,
    valor: str,
    cor_valor: str,
    comparacao: str,
    cor_comparacao: str,
    interpretacao: str,
    detalhe_secundario: str | None = None,
    data_base: str | None = None,
    apoios_curto: list[str] | None = None,
    destaques_comparacao: list[str] | None = None,
    classe_extra: str = "",
) -> None:
    def _limpar_html(texto: str | None) -> str:
        if texto is None:
            return ""
        texto_limpo = str(texto)
        # Decodifica entidades HTML repetidamente (cobre entradas duplamente escapadas).
        anterior = None
        while texto_limpo != anterior:
            anterior = texto_limpo
            texto_limpo = html.unescape(texto_limpo)

        # Remove tags HTML e resíduos de classe/código que possam vazar para a interface.
        texto_limpo = re.sub(r"(?is)</?\s*p[^>]*>", " ", texto_limpo)
        texto_limpo = re.sub(r"(?is)<[^>]+>", " ", texto_limpo)
        texto_limpo = re.sub(r"(?i)kpi-analitico-[\w-]+", " ", texto_limpo)
        texto_limpo = re.sub(r"(?i)\bp\s*class\s*=", " ", texto_limpo)
        texto_limpo = re.sub(r"(?i)\b/p\b", " ", texto_limpo)
        texto_limpo = texto_limpo.replace("<", " ").replace(">", " ")
        texto_limpo = re.sub(r"\s+", " ", texto_limpo).strip()
        return texto_limpo

    label_limpo = _limpar_html(label)
    valor_limpo = _limpar_html(valor)
    comparacao_limpa = _limpar_html(comparacao)
    interpretacao_limpa = _limpar_html(interpretacao)
    detalhe_limpo = _limpar_html(detalhe_secundario) if detalhe_secundario else ""
    data_base_limpa = _limpar_html(data_base) if data_base else ""
    comparacao_html = html.escape(comparacao_limpa)
    if destaques_comparacao:
        for trecho in destaques_comparacao:
            trecho_limpo = _limpar_html(trecho)
            if not trecho_limpo:
                continue
            trecho_escapado = html.escape(trecho_limpo)
            comparacao_html = comparacao_html.replace(
                trecho_escapado,
                f"<span class='kpi-analitico-comparacao-destaque'>{trecho_escapado}</span>",
            )

    with coluna:
        with st.container(border=True):
            secundario_html = (
                f"<p class='kpi-analitico-secundario'>{html.escape(detalhe_limpo)}</p>"
                if detalhe_limpo
                else ""
            )
            apoios_html = ""
            if apoios_curto:
                def _classe_apoio(texto_apoio: str) -> str:
                    base = _normalizar_coluna(texto_apoio)
                    if base.startswith("carteira:") or base.startswith("ibov:"):
                        return "kpi-analitico-apoio-forte"
                    if base.startswith("alto risco:") or base.startswith("baixo risco:"):
                        return "kpi-analitico-apoio-forte"
                    if base.startswith("cdi:"):
                        return "kpi-analitico-apoio-forte"
                    return "kpi-analitico-apoio-neutro"

                apoios = "".join(
                    f"<p class='kpi-analitico-apoio {_classe_apoio(_limpar_html(item))}'>{html.escape(_limpar_html(item))}</p>"
                    for item in apoios_curto
                    if item
                )
                if apoios:
                    apoios_html = f"<div class='kpi-analitico-apoios'>{apoios}</div>"
            rodape_base_html = (
                f"<p style='margin: 0.6rem 0 0 0; font-size: 0.70rem; color: #b0b8c1; border-top: 1px solid #f0f0f0; padding-top: 0.4rem;'>Base: {html.escape(data_base_limpa)}</p>"
                if data_base_limpa
                else ""
            )
            card_html = (
                f"<div class='kpi-analitico {html.escape(classe_extra)}'>"
                f"<p class='kpi-analitico-label'>{html.escape(label_limpo)}</p>"
                f"<p class='kpi-analitico-valor' style='color: {cor_valor};'>{html.escape(valor_limpo)}</p>"
                f"<p class='kpi-analitico-comparacao' style='color: {cor_comparacao};'>{comparacao_html}</p>"
                f"{apoios_html}"
                f"<p class='kpi-analitico-interpretacao'>{html.escape(interpretacao_limpa)}</p>"
                f"{secundario_html}"
                f"{rodape_base_html}"
                f"</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)


def _normalizar_serie_base_100(serie: pd.Series) -> pd.Series:
    serie_limpa = pd.to_numeric(serie, errors="coerce").dropna()
    if serie_limpa.empty:
        return serie_limpa
    primeiro = float(serie_limpa.iloc[0])
    if 95 <= primeiro <= 105:
        return serie_limpa
    if 0.95 <= primeiro <= 1.05:
        return serie_limpa * 100
    if -1 <= primeiro <= 1:
        return (1 + serie_limpa) * 100
    return serie_limpa


def _aplicar_layout_sparkline(fig: Any) -> Any:
    if fig is None:
        return None
    fig.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        height=55,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def _carregar_sparkline_ipca() -> Any | None:
    if go is None:
        return None
    raiz = Path(__file__).resolve().parent
    csv_path = raiz / "dados" / "macroeconomia" / "ipca.csv"
    if not csv_path.exists():
        return None
    try:
        df_raw = pd.read_csv(csv_path)
    except Exception:
        return None
    if df_raw.empty:
        return None
    col_data = _detectar_coluna(list(df_raw.columns), ("data", "date", "periodo", "mes"))
    col_valor = _detectar_coluna(list(df_raw.columns), ("valor", "ipca", "indice", "taxa"), excluir={col_data})
    if not col_data or not col_valor:
        return None
    df = df_raw[[col_data, col_valor]].rename(columns={col_data: "data", col_valor: "valor"})

    if df.empty:
        return None

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["data", "valor"]).sort_values("data").tail(24)
    if df.empty:
        return None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["valor"],
            mode="lines",
            line=dict(color="#c0392b", width=1.4),
            hoverinfo="skip",
        )
    )
    return _aplicar_layout_sparkline(fig)


def _carregar_sparkline_credito() -> Any | None:
    if go is None:
        return None
    alto_risco, baixo_risco = _carregar_inadimplencia_extremos()
    if alto_risco is None or baixo_risco is None:
        return None

    medio_risco = (alto_risco + baixo_risco) / 2
    df = pd.DataFrame(
        {
            "classe": ["baixo", "medio", "alto"],
            "taxa_pct": [baixo_risco, medio_risco, alto_risco],
            "cor": ["#1a7a4a", "#e67e22", "#c0392b"],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["taxa_pct"],
            y=df["classe"],
            orientation="h",
            marker=dict(color=df["cor"]),
            hoverinfo="skip",
        )
    )
    return _aplicar_layout_sparkline(fig)


def _carregar_sparkline_investimentos() -> Any | None:
    if go is None:
        return None
    raiz = Path(__file__).resolve().parent
    comparativo_path = raiz / "dados" / "investimentos" / "comparativo_carteira_benchmarks.csv"
    if not comparativo_path.exists():
        return None

    try:
        df = pd.read_csv(comparativo_path)
    except Exception:
        return None

    if df.empty:
        return None

    colunas = list(df.columns)
    col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
    col_carteira = _detectar_coluna(colunas, ("carteira", "buy_and_hold", "buy and hold", "retorno_carteira"))
    col_cdi = _detectar_coluna(colunas, ("proxy_cdi", "cdi", "posfixado", "pos_fixado", "pós_fixado"))
    if not col_data or not col_carteira or not col_cdi:
        return None

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df[col_carteira] = pd.to_numeric(df[col_carteira], errors="coerce")
    df[col_cdi] = pd.to_numeric(df[col_cdi], errors="coerce")
    df = df.dropna(subset=[col_data, col_carteira, col_cdi]).sort_values(col_data).tail(60)
    if df.empty:
        return None

    carteira_base100 = _normalizar_serie_base_100(df[col_carteira])
    cdi_base100 = _normalizar_serie_base_100(df[col_cdi])
    tamanho = min(len(df[col_data]), len(carteira_base100), len(cdi_base100))
    if tamanho == 0:
        return None

    datas = df[col_data].tail(tamanho)
    carteira_base100 = carteira_base100.tail(tamanho)
    cdi_base100 = cdi_base100.tail(tamanho)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=datas,
            y=carteira_base100,
            mode="lines",
            line=dict(color="#1f3b5c", width=1.6),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=datas,
            y=cdi_base100,
            mode="lines",
            line=dict(color="#aab8c6", width=1.2, dash="dash"),
            hoverinfo="skip",
        )
    )
    return _aplicar_layout_sparkline(fig)


@st.cache_data(show_spinner=False)
def _carregar_selic_atual() -> str | None:
    raiz = Path(__file__).resolve().parent
    db_path = raiz / "dados" / "macroeconomia" / "dados_economicos.db"
    if not db_path.exists():
        return None

    try:
        with sqlite3.connect(db_path) as conn:
            tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "selic" not in tabelas:
                return None

            colunas = [linha[1] for linha in conn.execute("PRAGMA table_info(selic)")]
            col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
            col_valor = _detectar_coluna(colunas, ("valor", "selic", "taxa", "indice"), excluir={col_data})
            if col_valor is None:
                return None

            if col_data:
                query = (
                    f'SELECT "{col_valor}" FROM selic '
                    f'WHERE "{col_valor}" IS NOT NULL ORDER BY date("{col_data}") DESC LIMIT 1'
                )
            else:
                query = f'SELECT "{col_valor}" FROM selic WHERE "{col_valor}" IS NOT NULL ORDER BY rowid DESC LIMIT 1'

            linha = conn.execute(query).fetchone()
            if not linha:
                return None

            valor = pd.to_numeric(linha[0], errors="coerce")
            if pd.isna(valor):
                return None

            valor = float(valor)
            if 0 <= valor <= 2:
                valor = valor * 12

            return f"{valor:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except sqlite3.Error:
        return None


@st.cache_data(show_spinner=False)
def _carregar_data_base_investimentos() -> str | None:
    raiz = Path(__file__).resolve().parent
    comparativo_path = raiz / "dados" / "investimentos" / "comparativo_carteira_benchmarks.csv"
    if not comparativo_path.exists():
        return None

    try:
        df = pd.read_csv(comparativo_path)
    except Exception:
        return None

    if df.empty:
        return None

    col_data = _detectar_coluna(list(df.columns), ("data", "date", "periodo", "mes"))
    if not col_data:
        return None

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data])
    if df.empty:
        return None

    return df[col_data].max().strftime("%d/%m/%Y")


@st.cache_data(show_spinner=False)
def _carregar_metricas_ipca_home() -> dict[str, Any] | None:
    raiz = Path(__file__).resolve().parent
    db_path = raiz / "dados" / "macroeconomia" / "dados_economicos.db"
    csv_path = raiz / "dados" / "macroeconomia" / "ipca.csv"

    df = pd.DataFrame()
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if "ipca" not in tabelas:
                    return None
                colunas = [linha[1] for linha in conn.execute("PRAGMA table_info(ipca)")]
                col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
                col_valor = _detectar_coluna(colunas, ("valor", "ipca", "indice", "taxa"), excluir={col_data})
                if not col_data or not col_valor:
                    return None
                df = pd.read_sql_query(
                    f'SELECT "{col_data}" AS data, "{col_valor}" AS valor FROM ipca',
                    conn,
                )
        except sqlite3.Error:
            return None

    elif csv_path.exists():
        try:
            df_raw = pd.read_csv(csv_path)
        except Exception:
            return None
        if df_raw.empty:
            return None
        col_data = _detectar_coluna(list(df_raw.columns), ("data", "date", "periodo", "mes"))
        col_valor = _detectar_coluna(list(df_raw.columns), ("valor", "ipca", "indice", "taxa"), excluir={col_data})
        if not col_data or not col_valor:
            return None
        df = df_raw[[col_data, col_valor]].rename(columns={col_data: "data", col_valor: "valor"})
    else:
        return None

    if df.empty:
        return None

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["data", "valor"]).sort_values("data")
    if df.empty:
        return None

    ultimo = float(df["valor"].iloc[-1])
    anterior = float(df["valor"].iloc[-2]) if len(df) > 1 else None
    data_base = df["data"].iloc[-1]
    data_anterior = df["data"].iloc[-2] if len(df) > 1 else None

    janela_12m = df.tail(12)["valor"]
    if janela_12m.empty:
        return None
    # IPCA 12M: acumulado composto dos últimos 12 meses.
    fatores = 1 + (janela_12m / 100)
    ipca_12m = float((fatores.prod() - 1) * 100)

    return {
        "ipca_12m": ipca_12m,
        "ipca_mensal": ultimo,
        "delta_mensal": (ultimo - anterior) if anterior is not None else None,
        "data_base": data_base.strftime("%d/%m/%Y"),
        "mes_ref_anterior": _formatar_mes_ano_pt_br(data_anterior),
    }


@st.cache_data(show_spinner=False)
def _carregar_data_base_ipca() -> str | None:
    metricas = _carregar_metricas_ipca_home()
    if metricas:
        return metricas.get("data_base")

    raiz = Path(__file__).resolve().parent
    db_path = raiz / "dados" / "macroeconomia" / "dados_economicos.db"
    csv_path = raiz / "dados" / "macroeconomia" / "ipca.csv"

    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if "ipca" not in tabelas:
                    return None
                colunas = [linha[1] for linha in conn.execute("PRAGMA table_info(ipca)")]
                col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
                if not col_data:
                    return None
                linha = conn.execute(
                    f'SELECT "{col_data}" FROM ipca WHERE "{col_data}" IS NOT NULL '
                    f'ORDER BY date("{col_data}") DESC LIMIT 1'
                ).fetchone()
                if not linha:
                    return None
                data = pd.to_datetime(linha[0], errors="coerce")
                if pd.isna(data):
                    return None
                return data.strftime("%d/%m/%Y")
        except sqlite3.Error:
            return None

    if not csv_path.exists():
        return None

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None
    if df.empty:
        return None

    col_data = _detectar_coluna(list(df.columns), ("data", "date", "periodo", "mes"))
    if not col_data:
        return None

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data])
    if df.empty:
        return None
    return df[col_data].max().strftime("%d/%m/%Y")


@st.cache_data(show_spinner=False)
def _carregar_metricas_investimentos_home() -> dict[str, Any] | None:
    raiz = Path(__file__).resolve().parent
    comparativo_path = raiz / "dados" / "investimentos" / "comparativo_carteira_benchmarks.csv"
    if not comparativo_path.exists():
        return None

    try:
        df = pd.read_csv(comparativo_path)
    except Exception:
        return None

    if df.empty:
        return None

    colunas = list(df.columns)
    col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
    col_carteira = _detectar_coluna(colunas, ("carteira", "buy_and_hold", "buy and hold", "retorno_carteira"))
    col_ibov = _detectar_coluna(colunas, ("ibov", "ibovespa"))
    col_cdi = _detectar_coluna(colunas, ("proxy_cdi", "cdi", "posfixado", "pos_fixado", "pós_fixado"))
    if not col_data or not col_carteira:
        return None

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data]).sort_values(col_data)
    if df.empty:
        return None

    retorno_carteira = _retorno_acumulado_serie(df[col_carteira])
    retorno_ibov = _retorno_acumulado_serie(df[col_ibov]) if col_ibov else None
    retorno_cdi = _retorno_acumulado_serie(df[col_cdi]) if col_cdi else None
    if retorno_carteira is None:
        return None

    return {
        "retorno_carteira": retorno_carteira,
        "retorno_ibov": retorno_ibov,
        "retorno_cdi": retorno_cdi,
        "vs_ibov_pp": (retorno_carteira - retorno_ibov) if retorno_ibov is not None else None,
        "data_base": df[col_data].max().strftime("%d/%m/%Y"),
    }


def _formatar_inteiro_br(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def _formatar_registros_mil(total: int) -> str:
    if total >= 1000:
        mil = total / 1000
        if abs(mil - round(mil)) < 0.05:
            return f"{int(round(mil))} mil"
        return f"{mil:.1f}".replace(".", ",") + " mil"
    return _formatar_inteiro_br(total)


@st.cache_data(show_spinner=False)
def _carregar_contexto_base_credito() -> str:
    raiz = Path(__file__).resolve().parent
    db_path = raiz / "dados" / "credito" / "risco_credito.db"
    if not db_path.exists():
        return "Base: não disponível"

    try:
        with sqlite3.connect(db_path) as conn:
            tabelas = [linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            if not tabelas:
                return "Base: não disponível"

            tabela = "credito_score" if "credito_score" in tabelas else tabelas[0]
            linha_total = conn.execute(f'SELECT COUNT(*) FROM "{tabela}"').fetchone()
            total = int(linha_total[0]) if linha_total and linha_total[0] is not None else 0
            if total > 0:
                return f"Base sintética: {_formatar_registros_mil(total)} registros"

            return "Base sintética de scoring do projeto"
    except sqlite3.Error:
        return "Base sintética de scoring do projeto"


@st.cache_data(show_spinner=False)
def _carregar_inadimplencia_extremos() -> tuple[float | None, float | None]:
    raiz = Path(__file__).resolve().parent
    db_path = raiz / "dados" / "credito" / "risco_credito.db"
    if not db_path.exists():
        return None, None

    try:
        with sqlite3.connect(db_path) as conn:
            tabelas = [linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            tabelas_norm = {_normalizar_coluna(t): t for t in tabelas}
            tabela_score = tabelas_norm.get("credito_score")
            if not tabela_score:
                return None, None

            colunas = [linha[1] for linha in conn.execute(f'PRAGMA table_info("{tabela_score}")')]
            colunas_norm = {_normalizar_coluna(c): c for c in colunas}
            col_class = colunas_norm.get("classificacao_risco")
            col_target = colunas_norm.get("seriousdlqin2yrs")
            if not col_class or not col_target:
                return None, None

            query = (
                f'SELECT lower(trim("{col_class}")) AS classe, AVG(CAST("{col_target}" AS REAL)) AS taxa '
                f'FROM "{tabela_score}" '
                f'WHERE "{col_class}" IS NOT NULL AND "{col_target}" IS NOT NULL '
                f'GROUP BY lower(trim("{col_class}"))'
            )
            dados = conn.execute(query).fetchall()
            alto, baixo = None, None
            for classe, taxa in dados:
                if taxa is None:
                    continue
                taxa_pct = float(taxa) * 100 if float(taxa) <= 1.5 else float(taxa)
                if str(classe).startswith("alto"):
                    alto = taxa_pct
                elif str(classe).startswith("baixo"):
                    baixo = taxa_pct
            return alto, baixo
    except sqlite3.Error:
        return None, None


@st.cache_data(show_spinner=False)
def _carregar_retorno_cdi_periodo() -> float | None:
    raiz = Path(__file__).resolve().parent
    comparativo_path = raiz / "dados" / "investimentos" / "comparativo_carteira_benchmarks.csv"
    if not comparativo_path.exists():
        return None
    try:
        df = pd.read_csv(comparativo_path)
    except Exception:
        return None
    if df.empty:
        return None

    colunas = list(df.columns)
    col_data = _detectar_coluna(colunas, ("data", "date", "periodo", "mes"))
    col_cdi = _detectar_coluna(colunas, ("proxy_cdi", "cdi", "posfixado", "pos_fixado", "pós_fixado"))
    if not col_cdi:
        return None

    if col_data:
        df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
        df = df.dropna(subset=[col_data]).sort_values(col_data)
    df[col_cdi] = pd.to_numeric(df[col_cdi], errors="coerce")
    serie = df[col_cdi].dropna()
    if serie.empty:
        return None

    primeiro = float(serie.iloc[0])
    ultimo = float(serie.iloc[-1])
    if 95 <= primeiro <= 105:
        return ((ultimo / 100) - 1) * 100
    if 0.95 <= primeiro <= 1.05:
        return (ultimo - 1) * 100
    return ultimo


def _renderizar_area_portfolio_v2(
    coluna,
    titulo: str,
    frase: str,
    pagina: str,
    key: str,
    cor_borda: str,
) -> None:
    with coluna:
        with st.container(border=True):
            st.markdown(
                (
                    f"<div style='border-left: 4px solid {html.escape(cor_borda)}; padding-left: 12px;'>"
                    f"<p class='portfolio-title'>{html.escape(titulo)}</p>"
                    f"<p class='portfolio-text'>{html.escape(frase)}</p>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )
            if st.button("Ver análise →", key=key, width="stretch"):
                st.switch_page(pagina)


def pagina_inicio() -> None:
    kpis = carregar_kpis_home()
    data_base_invest = _carregar_data_base_investimentos() or "Indisponível"

    metricas_ipca = _carregar_metricas_ipca_home()
    metricas_invest = _carregar_metricas_investimentos_home()

    st.markdown("<div style='padding-top: 0.3rem'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:1.6rem; font-weight:800; color:#1f3b5c; letter-spacing:-0.5px; margin:0; line-height:1.2;'>Dashboard Econômico</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:0.92rem; color:#4b5563; margin:0.3rem 0 0 0; line-height:1.4;'>Inflação, inadimplência e retorno de carteira analisados em perspectiva — cada indicador reflete sua própria janela temporal e base de dados.</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("<div style='height: 0.55rem;'></div>", unsafe_allow_html=True)

    st.markdown("### Destaques")
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    # Card 1: Macroeconomia.
    if metricas_ipca:
        ipca_12m_texto = _formatar_percentual_br(metricas_ipca["ipca_12m"])
        ipca_mensal_texto = _formatar_percentual_br(metricas_ipca["ipca_mensal"])
    else:
        ipca_12m_texto = "Indisponível"
        ipca_mensal_texto = kpis["ipca"].valor

    selic_atual = _carregar_selic_atual() or "n/d"
    _renderizar_kpi_analitico(
        col1,
        "IPCA 12 MESES",
        ipca_12m_texto,
        "#c0392b",
        "↑ Acima da meta BCB",
        "#c0392b",
        "Inflação segue pressionada acima da meta",
        detalhe_secundario=f"Mensal: {ipca_mensal_texto} | Selic: {selic_atual}",
        data_base="dez/2024",
    )

    # Card 2: Crédito.
    alto_risco, baixo_risco = _carregar_inadimplencia_extremos()
    if alto_risco is None or baixo_risco is None:
        alto_risco = 54.1  # TODO: usar cálculo real dos extremos quando não houver coluna compatível.
        baixo_risco = 4.2  # TODO: usar cálculo real dos extremos quando não houver coluna compatível.
    media_geral_credito = _valor_percentual_para_float(kpis["inadimplencia"].valor) if kpis.get("inadimplencia") else None
    media_geral_credito_txt = _formatar_percentual_br(media_geral_credito) if media_geral_credito is not None else "n/d"
    _renderizar_kpi_analitico(
        col2,
        "INADIMPLÊNCIA — ALTO RISCO",
        _formatar_percentual_br(alto_risco, casas=1) if alto_risco is not None else "Indisponível",
        "#c0392b",
        f"↓ Baixo risco: {_formatar_percentual_br(baixo_risco, casas=1)}" if baixo_risco is not None else "↓ Baixo risco: n/d",
        "#1a7a4a",
        "Score segmenta inadimplência 13x entre classes extremas",
        detalhe_secundario=f"Base: 150k registros | média geral: {media_geral_credito_txt}",
        data_base="Give Me Some Credit — Kaggle",
    )

    # Card 3: Investimentos.
    if metricas_invest:
        carteira_retorno = metricas_invest["retorno_carteira"]
        retorno_ibov = metricas_invest["retorno_ibov"]
        retorno_cdi = metricas_invest["retorno_cdi"]
    else:
        carteira_retorno = _valor_percentual_para_float(kpis["rentabilidade"].valor)
        retorno_ibov = None
        retorno_cdi = _carregar_retorno_cdi_periodo()

    vs_cdi = (carteira_retorno - retorno_cdi) if (carteira_retorno is not None and retorno_cdi is not None) else None
    valor_principal_invest = _formatar_percentual_br(carteira_retorno, mostrar_sinal=True) if carteira_retorno is not None else "Indisponível"
    carteira_txt = _formatar_percentual_br(carteira_retorno, mostrar_sinal=True) if carteira_retorno is not None else "n/d"
    ibov_txt = _formatar_percentual_br(retorno_ibov, mostrar_sinal=True) if retorno_ibov is not None else "n/d"
    cdi_txt = _formatar_percentual_br(retorno_cdi, mostrar_sinal=True) if retorno_cdi is not None else "n/d"
    comp_invest = (
        f"↑ {_formatar_pp_br(vs_cdi)} acima do CDI"
        if vs_cdi is not None
        else "↑ Comparativo com CDI indisponível"
    )
    _renderizar_kpi_analitico(
        col3,
        "RETORNO ACUMULADO",
        valor_principal_invest,
        "#1a7a4a",
        comp_invest,
        "#1a7a4a",
        "Carteira supera benchmark consistentemente (2020–2026)",
        detalhe_secundario=f"IBOV: {ibov_txt} | CDI: {cdi_txt}",
        data_base=f"até {data_base_invest}",
    )

    st.markdown("### Frentes de análise")
    st.markdown(
        "<p style='font-size:0.85rem; color:#6b7280; margin:-0.5rem 0 0.8rem 0; line-height:1.5;'>O cenário macro define o custo do dinheiro, o crédito mede o risco de quem toma, e a carteira mostra o retorno de quem investe.</p>",
        unsafe_allow_html=True,
    )
    area1, area2, area3 = st.columns([1, 1, 1], gap="medium")

    _renderizar_area_portfolio_v2(
        area1,
        "Macroeconomia",
        "IPCA e Selic em perspectiva para leitura de inflação, juros e seus efeitos no cenário.",
        "pages/macroeconomia.py",
        "home_nav_macro",
        "#1f3b5c",
    )
    _renderizar_area_portfolio_v2(
        area2,
        "Crédito",
        "Segmentação de risco e inadimplência para apoiar concessão, monitoramento e priorização.",
        "pages/credito.py",
        "home_nav_credito",
        "#c0622a",
    )
    _renderizar_area_portfolio_v2(
        area3,
        "Investimentos",
        "Performance da carteira frente a benchmarks, com foco em retorno relativo e consistência.",
        "pages/investimentos.py",
        "home_nav_invest",
        "#1a7a4a",
    )

    st.markdown(
        """
        <div class="home-footer">
            Desenvolvido por Caio César Merzbacher · Ciências Econômicas USCS · CPA-10 | CPA-20<br>
            <a href="https://github.com/CaioMerz" target="_blank">GitHub</a>
            <a href="https://www.linkedin.com/" target="_blank">LinkedIn</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


paginas = [
    st.Page(pagina_inicio, title="Inicio"),
    st.Page("pages/macroeconomia.py", title="Macroeconomia"),
    st.Page("pages/credito.py", title="Credito"),
    st.Page("pages/investimentos.py", title="Investimentos"),
    st.Page("pages/sobre.py", title="Sobre"),
]

navegacao = st.navigation(paginas, position="sidebar")
st.sidebar.markdown(
    "<p style='font-size:0.7rem; color:#888; padding: 0.5rem 0.8rem; margin:0; border-bottom: 1px solid #dde3ea; margin-bottom: 0.5rem;'>ANÁLISE FINANCEIRA</p>",
    unsafe_allow_html=True,
)
navegacao.run()



