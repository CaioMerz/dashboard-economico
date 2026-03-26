from pathlib import Path
import unicodedata

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
DADOS_DIR = BASE_DIR / "dados" / "investimentos"
ARQ_COMPARATIVO = DADOS_DIR / "comparativo_carteira_benchmarks.csv"


def _normalizar(texto: str) -> str:
    texto = str(texto).strip().lower()
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def _detectar_coluna_por_chaves(colunas: list[str], chaves: tuple[str, ...]) -> str | None:
    for chave in chaves:
        for coluna in colunas:
            if chave in _normalizar(coluna):
                return coluna
    return None


def _retorno_percentual(serie: pd.Series) -> float | None:
    serie_limpa = pd.to_numeric(serie, errors="coerce").dropna()
    if serie_limpa.empty:
        return None

    primeiro = float(serie_limpa.iloc[0])
    ultimo = float(serie_limpa.iloc[-1])

    if 95 <= primeiro <= 105:
        return ((ultimo / 100) - 1) * 100
    if 0.95 <= primeiro <= 1.05:
        return (ultimo - 1) * 100
    if -0.1 <= primeiro <= 0.1 and -1 <= ultimo <= 1:
        return ultimo * 100
    return ultimo


def _formatar_percentual(valor: float | None) -> str:
    if valor is None or pd.isna(valor):
        return "Indisponível"
    return f"{valor:.2f}%"


def _carregar_base_comparativa() -> tuple[pd.DataFrame | None, str | None]:
    if ARQ_COMPARATIVO.exists():
        try:
            return pd.read_csv(ARQ_COMPARATIVO), ARQ_COMPARATIVO.name
        except Exception:
            return None, ARQ_COMPARATIVO.name
    return None, None


def renderizar_pagina() -> None:
    st.title("Investimentos")
    st.markdown("Análise de performance da carteira em comparação com benchmarks de mercado.")

    df, origem = _carregar_base_comparativa()

    if origem is None:
        st.warning("Arquivo comparativo de benchmarks não encontrado.")
        st.info(
            "Copie `comparativo_carteira_benchmarks.csv` para `dados/investimentos/` "
            "para habilitar a comparação da carteira com IBOV e CDI/proxy."
        )
        return
    if df is None:
        st.warning("Não foi possível ler a base de investimentos")
        return

    colunas = list(df.columns)
    coluna_data = _detectar_coluna_por_chaves(colunas, ("data", "date", "periodo"))
    coluna_carteira = _detectar_coluna_por_chaves(colunas, ("carteira", "portfolio", "buy_and_hold"))
    coluna_ibov = _detectar_coluna_por_chaves(colunas, ("ibov", "ibovespa"))
    coluna_cdi = _detectar_coluna_por_chaves(
        colunas,
        ("cdi", "pos_fixado", "pos-fixado", "posfixado", "proxy"),
    )

    if coluna_data is None:
        st.warning("Coluna de data não encontrada na base de investimentos")
        return
    if coluna_carteira is None:
        st.warning("Coluna da carteira não encontrada na base de investimentos")
        return

    faltantes = []
    if coluna_ibov is None:
        faltantes.append("IBOV")
    if coluna_cdi is None:
        faltantes.append("CDI/proxy")

    if faltantes:
        st.warning(
            "Não foi possível montar o comparativo completo da carteira com benchmarks. "
            f"Séries ausentes: {', '.join(faltantes)}."
        )
        return

    colunas_uso = [coluna_data, coluna_carteira, coluna_ibov, coluna_cdi]
    df = df[colunas_uso].copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")

    for coluna in [coluna_carteira, coluna_ibov, coluna_cdi]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df = df.dropna(subset=[coluna_data, coluna_carteira, coluna_ibov, coluna_cdi]).sort_values(coluna_data)
    if df.empty:
        st.warning("Base de investimentos sem dados válidos para análise comparativa")
        return

    retorno_carteira = _retorno_percentual(df[coluna_carteira])
    retorno_ibov = _retorno_percentual(df[coluna_ibov])
    retorno_cdi = _retorno_percentual(df[coluna_cdi])

    diff_ibov = (retorno_carteira - retorno_ibov) if retorno_carteira is not None and retorno_ibov is not None else None
    diff_cdi = (retorno_carteira - retorno_cdi) if retorno_carteira is not None and retorno_cdi is not None else None
    data_base = df[coluna_data].max()

    serie_carteira = pd.to_numeric(df[coluna_carteira], errors="coerce").dropna()
    serie_ret = serie_carteira.pct_change().dropna()
    volatilidade_anualizada = None
    sharpe_ratio = None
    drawdown_max = None

    if not serie_ret.empty:
        delta = df[coluna_data].sort_values().diff().dt.days.median()
        if pd.isna(delta):
            fator_anual = 12
        elif delta <= 2:
            fator_anual = 252
        elif delta <= 10:
            fator_anual = 52
        else:
            fator_anual = 12

        volatilidade_anualizada = float(serie_ret.std() * (fator_anual ** 0.5) * 100)
        if serie_ret.std() > 0:
            sharpe_ratio = float((serie_ret.mean() * fator_anual) / (serie_ret.std() * (fator_anual ** 0.5)))

        indice_base = serie_carteira / serie_carteira.iloc[0]
        max_acumulado = indice_base.cummax()
        drawdown = (indice_base / max_acumulado) - 1
        drawdown_max = float(drawdown.min() * 100)

    retorno_anual = pd.Series(dtype=float)
    retorno_anual_labels: list[str] = []
    ano_corrente_parcial = False
    df_ret_anual = df[[coluna_data, coluna_carteira]].dropna().copy()
    if not df_ret_anual.empty:
        df_ret_anual["ano"] = df_ret_anual[coluna_data].dt.year
        anual = df_ret_anual.groupby("ano")[coluna_carteira].agg(["first", "last"])
        retorno_anual = ((anual["last"] / anual["first"]) - 1) * 100
        ultimo_registro = df_ret_anual[coluna_data].max()
        if pd.notna(ultimo_registro):
            ano_maximo = int(retorno_anual.index.max())
            ano_corrente = int(ultimo_registro.year)
            fim_ano = pd.Timestamp(year=ano_corrente, month=12, day=31)
            ano_corrente_parcial = ano_maximo == ano_corrente and ultimo_registro < fim_ano

        for ano in retorno_anual.index:
            if ano_corrente_parcial and int(ano) == int(retorno_anual.index.max()):
                retorno_anual_labels.append(f"{int(ano)} YTD")
            else:
                retorno_anual_labels.append(str(int(ano)))

    col_esquerda, col_direita = st.columns([3, 1.2], gap="medium")

    with col_esquerda:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.set_facecolor("#ffffff")
        ax.plot(df[coluna_data], df[coluna_carteira], label="Carteira", linewidth=2.8, color="#1f3b5c", zorder=3)
        ax.plot(df[coluna_data], df[coluna_ibov], label="IBOV", linewidth=1.8, color="#c0392b", zorder=2)
        ax.plot(
            df[coluna_data],
            df[coluna_cdi],
            label="CDI (proxy)",
            linewidth=1.4,
            linestyle="--",
            color="#27ae60",
            alpha=0.95,
            zorder=1,
        )

        ax.set_title("Carteira vs Benchmarks — Evolução histórica", fontsize=11, fontweight="semibold")
        ax.set_xlabel("Data", fontsize=9)
        ax.set_ylabel("Índice base 100", fontsize=9)
        ax.tick_params(axis="both", labelsize=8.5, colors="#4b5563")
        ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.18, color="#94a3b8")
        ax.legend(frameon=False, fontsize=9, loc="best")
        for spine in ax.spines.values():
            spine.set_color("#d1d5db")
        fig.autofmt_xdate()
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

        if not retorno_anual.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 3.8))
            cores = ["#1a7a4a" if v >= 0 else "#c0392b" for v in retorno_anual.values]
            ax2.bar(retorno_anual_labels, retorno_anual.values, color=cores)
            ax2.set_facecolor("#ffffff")
            titulo_anual = "Retorno anual da carteira (%)"
            if ano_corrente_parcial:
                titulo_anual += " + ano corrente (YTD)"
            ax2.set_title(titulo_anual, fontsize=10.5, fontweight="semibold")
            ax2.set_xlabel("Ano", fontsize=9)
            ax2.set_ylabel("Retorno (%)", fontsize=9)
            ax2.tick_params(axis="both", labelsize=8.5, colors="#4b5563")
            ax2.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.18, color="#94a3b8")
            for spine in ax2.spines.values():
                spine.set_color("#d1d5db")
            fig2.tight_layout()
            st.pyplot(fig2, width="stretch")
            plt.close(fig2)

    with col_direita:
        with st.container(border=True):
            st.markdown("#### Resumo")
            st.metric("Retorno acumulado da carteira", _formatar_percentual(retorno_carteira))
            st.markdown(f"**Carteira vs IBOV:** {f'{diff_ibov:.2f} p.p.' if diff_ibov is not None else 'Indisponível'}")
            st.markdown(f"**Carteira vs CDI/proxy:** {f'{diff_cdi:.2f} p.p.' if diff_cdi is not None else 'Indisponível'}")
            st.markdown(
                f"**Retorno/volatilidade (rf=0):** {f'{sharpe_ratio:.2f}' if sharpe_ratio is not None else 'Indisponível'}"
            )
            st.markdown(f"**Drawdown máximo:** {f'{drawdown_max:.2f}%' if drawdown_max is not None else 'Indisponível'}")
            st.markdown(
                f"**Volatilidade anualizada:** {f'{volatilidade_anualizada:.2f}%' if volatilidade_anualizada is not None else 'Indisponível'}"
            )
            st.markdown(f"**Data-base:** {data_base:%d/%m/%Y}")
            st.markdown(
                "**Metodologia:** carteira hipotética em estratégia buy and hold, "
                "calculada com dados reais de mercado."
            )
            st.markdown(
                "A comparação com IBOV e CDI mostra o retorno relativo da estratégia. "
                "A leitura conjunta de volatilidade, relação retorno/volatilidade e drawdown reforça a avaliação de consistência no período."
            )


renderizar_pagina()
