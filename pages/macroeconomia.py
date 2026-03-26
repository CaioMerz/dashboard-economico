from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import streamlit as st


DB_PATH = Path(__file__).resolve().parents[1] / "dados" / "macroeconomia" / "dados_economicos.db"


def carregar_series_macro(db_path: Path) -> pd.DataFrame:
    """Carrega e prepara as series de IPCA e Selic com join por data."""
    with sqlite3.connect(db_path) as conn:
        tabelas = {
            linha[0]
            for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }

        faltantes = [nome for nome in ("ipca", "selic") if nome not in tabelas]
        if faltantes:
            raise ValueError(f"Tabelas ausentes na base: {', '.join(faltantes)}")

        query = """
            SELECT
                i.data AS data,
                i.valor AS ipca,
                s.valor AS selic
            FROM ipca AS i
            INNER JOIN selic AS s
                ON i.data = s.data
            ORDER BY i.data ASC
        """
        df = pd.read_sql_query(query, conn)

    if df.empty:
        raise ValueError("Base macroeconômica sem dados após o JOIN entre IPCA e Selic")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["ipca"] = pd.to_numeric(df["ipca"], errors="coerce")
    df["selic"] = pd.to_numeric(df["selic"], errors="coerce")

    df = df.dropna(subset=["data", "ipca", "selic"]).sort_values("data")
    if df.empty:
        raise ValueError("Dados macroeconômicos inválidos após tratamento")

    return df


def renderizar_pagina() -> None:
    st.markdown("## Macroeconomia")
    st.markdown(
        "Visão objetiva da relação entre inflação (IPCA) e taxa de juros (Selic) no Brasil."
    )

    if not DB_PATH.exists():
        st.warning("Base macroeconômica não encontrada")
        return

    try:
        df = carregar_series_macro(DB_PATH)
    except ValueError as erro:
        st.warning(str(erro))
        return
    except sqlite3.Error:
        st.warning("Não foi possível ler a base macroeconômica")
        return

    correlacao = df["ipca"].corr(df["selic"], method="pearson")
    correlacao_defasada_6m = None
    df_lag = df[["ipca", "selic"]].copy()
    df_lag["selic_lag_6m"] = df_lag["selic"].shift(6)
    df_lag = df_lag.dropna(subset=["ipca", "selic_lag_6m"])
    if len(df_lag) >= 12:
        correlacao_defasada_6m = df_lag["ipca"].corr(df_lag["selic_lag_6m"], method="pearson")
    ultima_data = df["data"].max()

    col_esquerda, col_direita = st.columns([3, 1.2], gap="medium")

    with col_esquerda:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.set_facecolor("#ffffff")
        ax.plot(
            df["data"],
            df["ipca"],
            label="IPCA",
            linewidth=3.0,
            color="#1f3b5c",
            zorder=3,
        )
        ax.plot(
            df["data"],
            df["selic"],
            label="Selic",
            linewidth=2.0,
            linestyle="--",
            color="#2f2f2f",
            alpha=0.95,
            zorder=2,
        )
        ax.set_title("IPCA e Selic — Série histórica (2015–2024)", fontsize=11, fontweight="semibold")
        ax.set_xlabel("Data", fontsize=9)
        ax.set_ylabel("Variação mensal (%)", fontsize=9)
        ax.tick_params(axis="both", labelsize=8.5, colors="#374151")
        ax.grid(True, linestyle="--", linewidth=0.65, alpha=0.14, color="#94a3b8")
        ax.legend(frameon=False, fontsize=9, loc="best")
        for spine in ax.spines.values():
            spine.set_color("#c5ced8")
        fig.autofmt_xdate()
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

        df_aux = df.copy()
        fator_ipca = 1 + (df_aux["ipca"] / 100)
        df_aux["ipca_12m"] = (fator_ipca.rolling(window=12).apply(lambda x: x.prod(), raw=True) - 1) * 100
        meta_bc = 3.0
        df_aux = df_aux.dropna(subset=["ipca_12m"])
        fig2, ax2 = plt.subplots(figsize=(10, 3.6))
        ax2.set_facecolor("#ffffff")
        ax2.plot(
            df_aux["data"],
            df_aux["ipca_12m"],
            linewidth=2.2,
            color="#1f3b5c",
            zorder=3,
            label="IPCA acumulado em 12 meses",
        )
        ax2.axhline(
            meta_bc,
            color="#c0392b",
            linestyle="--",
            linewidth=1.0,
            alpha=0.9,
            label="Referência visual (3,0%)",
        )
        ax2.set_title("IPCA acumulado em 12 meses vs referência de 3,0%", fontsize=10.5, fontweight="semibold")
        ax2.set_xlabel("Data", fontsize=9)
        ax2.set_ylabel("Variação acumulada em 12 meses (%)", fontsize=9)
        ax2.tick_params(axis="both", labelsize=8.5, colors="#374151")
        ax2.grid(True, linestyle="--", linewidth=0.6, alpha=0.13, color="#94a3b8")
        ax2.legend(frameon=False, fontsize=8.5, loc="best")
        for spine in ax2.spines.values():
            spine.set_color("#c5ced8")
        fig2.autofmt_xdate()
        fig2.tight_layout()
        st.pyplot(fig2, width="stretch")
        plt.close(fig2)

    with col_direita:
        with st.container(border=True):
            st.markdown("#### Resumo")
            if correlacao_defasada_6m is not None and pd.notna(correlacao_defasada_6m):
                st.metric("Correlação defasada (Selic t-6 vs IPCA t)", f"{correlacao_defasada_6m:.2f}")
            else:
                st.metric("Correlação defasada (Selic t-6 vs IPCA t)", "Indisponível")

            st.markdown(f"**Base de dados atualizada até:** {ultima_data:%d/%m/%Y}")
            if pd.notna(correlacao):
                st.markdown(f"**Correlação contemporânea de referência:** {correlacao:.2f}")
            st.markdown(
                "O foco analítico está na associação com defasagem de seis meses entre Selic e IPCA. "
                "Essa leitura é descritiva e deve ser interpretada em conjunto com o contexto macroeconômico, "
                "sem inferir causalidade isolada entre as séries."
            )
            st.markdown("Nota: a linha de 3,0% é uma referência visual fixa e não a meta histórica ano a ano.")


renderizar_pagina()
