from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import streamlit as st


DB_PATH = Path(__file__).resolve().parents[1] / "dados" / "credito" / "risco_credito.db"


def _colunas_tabela(conn: sqlite3.Connection, tabela: str) -> set[str]:
    return {linha[1] for linha in conn.execute(f"PRAGMA table_info('{tabela}')")}


def _carregar_dados(conn: sqlite3.Connection) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Carrega apenas dados necessarios para os KPIs e grafico."""
    tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    df_raw = None
    if "credito_raw" in tabelas:
        colunas_raw = _colunas_tabela(conn, "credito_raw")
        colunas = [col for col in ["SeriousDlqin2yrs"] if col in colunas_raw]
        if colunas:
            df_raw = pd.read_sql_query(
                f"SELECT {', '.join(colunas)} FROM credito_raw",
                conn,
            )

    df_score = None
    if "credito_score" in tabelas:
        colunas_score = _colunas_tabela(conn, "credito_score")
        colunas = [
            col
            for col in ["SeriousDlqin2yrs", "classificacao_risco", "score_risco"]
            if col in colunas_score
        ]
        if colunas:
            df_score = pd.read_sql_query(
                f"SELECT {', '.join(colunas)} FROM credito_score",
                conn,
            )

    return df_raw, df_score


def _formatar_percentual(valor: float | None) -> str:
    if valor is None or pd.isna(valor):
        return "Indisponível"
    return f"{valor:.2f}%"


def _formatar_inteiro(valor: int | None) -> str:
    if valor is None:
        return "Indisponível"
    return f"{valor:,}".replace(",", ".")


def renderizar_pagina() -> None:
    st.title("Crédito")
    st.markdown(
        "Análise de inadimplência e segmentação de risco com base em score explicável."
    )

    if not DB_PATH.exists():
        st.warning("Base de crédito não encontrada")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            df_raw, df_score = _carregar_dados(conn)
    except sqlite3.Error:
        st.warning("Não foi possível ler a base de crédito")
        return

    if df_raw is None and df_score is None:
        st.warning("Tabelas de crédito não encontradas ou sem colunas necessárias")
        return

    taxa_inadimplencia = None
    if df_raw is not None and "SeriousDlqin2yrs" in df_raw.columns:
        serie_raw = pd.to_numeric(df_raw["SeriousDlqin2yrs"], errors="coerce").dropna()
        if not serie_raw.empty:
            taxa_inadimplencia = float(serie_raw.mean() * 100)

    df_risco_plot = pd.DataFrame()
    inad_baixo_risco = None
    inad_alto_risco = None
    multiplicador_extremos = None
    score_medio = None
    score_serie = pd.Series(dtype=float)

    if df_score is not None:
        if "score_risco" in df_score.columns:
            score_serie = pd.to_numeric(df_score["score_risco"], errors="coerce").dropna()
            if not score_serie.empty:
                score_medio = float(score_serie.mean())

        if "classificacao_risco" in df_score.columns and "SeriousDlqin2yrs" in df_score.columns:
            df_risco_plot = df_score[["classificacao_risco", "SeriousDlqin2yrs"]].copy()
            df_risco_plot["classificacao_risco"] = (
                df_risco_plot["classificacao_risco"].astype(str).str.strip().str.lower()
            )
            df_risco_plot["SeriousDlqin2yrs"] = pd.to_numeric(df_risco_plot["SeriousDlqin2yrs"], errors="coerce")
            df_risco_plot = df_risco_plot.dropna(subset=["classificacao_risco", "SeriousDlqin2yrs"])
            if not df_risco_plot.empty:
                taxa_baixo = (
                    df_risco_plot.loc[
                        df_risco_plot["classificacao_risco"].str.startswith("baixo"),
                        "SeriousDlqin2yrs",
                    ]
                    .mean()
                )
                taxa_alto = (
                    df_risco_plot.loc[
                        df_risco_plot["classificacao_risco"].str.startswith("alto"),
                        "SeriousDlqin2yrs",
                    ]
                    .mean()
                )
                if pd.notna(taxa_baixo):
                    inad_baixo_risco = float(taxa_baixo * 100)
                if pd.notna(taxa_alto):
                    inad_alto_risco = float(taxa_alto * 100)
                if (
                    inad_alto_risco is not None
                    and inad_baixo_risco is not None
                    and inad_baixo_risco > 0
                ):
                    multiplicador_extremos = inad_alto_risco / inad_baixo_risco

    if taxa_inadimplencia is None and not df_risco_plot.empty:
        taxa_inadimplencia = float(df_risco_plot["SeriousDlqin2yrs"].mean() * 100)

    if df_risco_plot.empty and score_serie.empty:
        st.warning("A base de crédito não possui colunas suficientes para os gráficos analíticos.")
        return

    col_esquerda, col_direita = st.columns([3, 1.2], gap="medium")

    with col_esquerda:
        if not df_risco_plot.empty:
            taxas = df_risco_plot.groupby("classificacao_risco")["SeriousDlqin2yrs"].mean() * 100
            ordem = ["baixo risco", "medio risco", "alto risco"]
            categorias = [c for c in ordem if c in taxas.index] + [c for c in taxas.index if c not in ordem]
            taxas = taxas.reindex(categorias)

            fig1, ax1 = plt.subplots(figsize=(10, 4.5))
            paleta = {
                "baixo risco": "#7f8c8d",
                "medio risco": "#1f3b5c",
                "alto risco": "#c0392b",
            }
            cores = [paleta.get(categoria, "#6b7280") for categoria in taxas.index]
            barras = ax1.bar(taxas.index, taxas.values, color=cores)
            ax1.set_facecolor("#ffffff")
            ax1.set_title("Inadimplência por faixa de risco", fontsize=11, fontweight="semibold")
            ax1.set_xlabel("Classificação de score", fontsize=9)
            ax1.set_ylabel("Inadimplência média (%)", fontsize=9)
            ax1.tick_params(axis="both", labelsize=8.5, colors="#4b5563")
            ax1.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.18, color="#94a3b8")
            for spine in ax1.spines.values():
                spine.set_color("#d1d5db")

            for barra in barras:
                valor = barra.get_height()
                ax1.text(
                    barra.get_x() + barra.get_width() / 2,
                    valor,
                    f"{valor:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=8.5,
                    color="#374151",
                )

            fig1.tight_layout()
            st.pyplot(fig1, width="stretch")
            plt.close(fig1)

        if not score_serie.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 3.8))
            ax2.hist(
                score_serie,
                bins=35,
                color="#1f3b5c",
                alpha=0.75,
                edgecolor="#ffffff",
                linewidth=0.4,
            )
            ax2.set_facecolor("#ffffff")
            ax2.set_title("Distribuição real de score da base", fontsize=10.5, fontweight="semibold")
            ax2.set_xlabel("Score de risco", fontsize=9)
            ax2.set_ylabel("Frequência", fontsize=9)
            ax2.tick_params(axis="both", labelsize=8.5, colors="#4b5563")
            ax2.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.15, color="#94a3b8")
            for spine in ax2.spines.values():
                spine.set_color("#d1d5db")
            fig2.tight_layout()
            st.pyplot(fig2, width="stretch")
            plt.close(fig2)
            st.caption(
                "Nota: o eixo X representa o score de risco calculado para cada registro da base; "
                "o gráfico mostra a distribuição dessa pontuação na amostra."
            )
        else:
            st.info("A coluna de score não está disponível na base atual.")

    with col_direita:
        with st.container(border=True):
            st.markdown("#### Resumo")
            st.metric("Inadimplência média da base", _formatar_percentual(taxa_inadimplencia))
            st.metric(
                "Diferença de inadimplência (alto vs baixo risco)",
                f"{multiplicador_extremos:.1f}x" if multiplicador_extremos is not None else "Indisponível",
            )
            st.metric("Inadimplência no alto risco", _formatar_percentual(inad_alto_risco))
            st.metric("Inadimplência no baixo risco", _formatar_percentual(inad_baixo_risco))
            st.markdown("**Origem da base:** Give Me Some Credit — Kaggle, 2011")
            st.markdown(
                "A segmentação de score separa grupos com comportamento de pagamento distinto. "
                "Esse recorte apoia decisões de concessão, monitoramento e priorização de carteira."
            )
            if score_medio is not None:
                st.caption(f"Score médio observado na base: {score_medio:.1f}")


renderizar_pagina()
