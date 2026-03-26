"""Leitura e calculo dos KPIs da Home."""

from __future__ import annotations

import csv
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class KpiData:
    """Representa um KPI pronto para exibicao."""

    valor: str
    delta: str | None
    fonte: str
    disponivel: bool
    microtexto: str


def carregar_kpis_home(base_dir: Path | None = None) -> dict[str, KpiData]:
    """Carrega os tres KPIs da Home com fallback e tratamento amigavel."""
    root = base_dir or Path(__file__).resolve().parents[1]
    return {
        "ipca": carregar_ipca_atual(root),
        "inadimplencia": carregar_inadimplencia(root),
        "rentabilidade": carregar_rentabilidade_carteira(root),
    }


def carregar_ipca_atual(base_dir: Path) -> KpiData:
    """Carrega o ultimo IPCA, priorizando o banco SQLite."""
    db_path = base_dir / "dados" / "macroeconomia" / "dados_economicos.db"
    csv_path = base_dir / "dados" / "macroeconomia" / "ipca.csv"

    if db_path.exists():
        resultado_db = _ipca_do_banco(db_path)
        if resultado_db.disponivel:
            return resultado_db

    if csv_path.exists():
        return _ipca_do_csv_tabular(csv_path)

    return _indisponivel("Arquivo de IPCA ausente")


def carregar_inadimplencia(base_dir: Path) -> KpiData:
    """Calcula taxa media de inadimplencia e compara com grupo de baixo risco."""
    db_path = base_dir / "dados" / "credito" / "risco_credito.db"
    if not db_path.exists():
        return _indisponivel("Arquivo de credito ausente")

    try:
        with sqlite3.connect(db_path) as conn:
            tabela, coluna = _escolher_tabela_coluna_inadimplencia(conn)
            if tabela is None or coluna is None:
                return _indisponivel("Coluna de inadimplencia nao encontrada")

            media_base = conn.execute(
                f'SELECT AVG(CAST("{coluna}" AS REAL)) FROM "{tabela}" WHERE "{coluna}" IS NOT NULL'
            ).fetchone()[0]
            if media_base is None:
                return _indisponivel("Sem valores validos de inadimplencia")

            taxa_base_pct = _to_percent(float(media_base))

            # Comparacao coerente com a propria base: inadimplencia do grupo "baixo risco".
            taxa_baixo_risco_pct = _inadimplencia_baixo_risco(conn)
            delta = (
                _formatar_delta(taxa_base_pct - taxa_baixo_risco_pct, sufixo=" p.p.")
                if taxa_baixo_risco_pct is not None
                else None
            )
            microtexto = (
                "Diferença da taxa média da base em relação ao grupo de baixo risco."
                if taxa_baixo_risco_pct is not None
                else "Taxa média de inadimplência da base analisada."
            )

            return KpiData(
                valor=_formatar_percentual(taxa_base_pct),
                delta=delta,
                fonte=f"{db_path.name}:{tabela}.{coluna}",
                disponivel=True,
                microtexto=microtexto,
            )
    except sqlite3.Error:
        return _indisponivel("Erro ao ler banco de credito")


def carregar_rentabilidade_carteira(base_dir: Path) -> KpiData:
    """Calcula retorno acumulado da carteira e delta vs IBOV (p.p.)."""
    comparativo_path = base_dir / "dados" / "investimentos" / "comparativo_carteira_benchmarks.csv"
    if comparativo_path.exists():
        resultado = _rentabilidade_do_comparativo(comparativo_path)
        if resultado.disponivel:
            return resultado

    csv_path = base_dir / "dados" / "investimentos" / "carteira_consolidada.csv"
    if not csv_path.exists():
        return _indisponivel("Arquivo da carteira ausente")

    try:
        linhas = _ler_csv_dict(csv_path)
        if not linhas:
            return _indisponivel("CSV da carteira vazio")

        colunas = list(linhas[0].keys())
        coluna_data = _escolher_coluna_data(colunas)
        coluna_carteira = _escolher_coluna_por_chaves(
            colunas,
            ("carteira_buy_and_hold", "carteira", "portfolio", "retorno", "desempenho"),
            excluir=(coluna_data,),
        )
        if coluna_carteira is None:
            return _indisponivel("Coluna da carteira nao encontrada")

        serie_carteira = _extrair_serie(linhas, coluna_carteira, coluna_data)
        if not serie_carteira:
            return _indisponivel("Sem valores validos da carteira")

        retorno = _retorno_acumulado_percentual(serie_carteira)
        return KpiData(
            valor=_formatar_percentual(retorno),
            delta=None,
            fonte=f"{csv_path.name}:{coluna_carteira}",
            disponivel=True,
            microtexto="Retorno acumulado da carteira no período disponível.",
        )
    except (OSError, csv.Error):
        return _indisponivel("Erro ao ler CSV da carteira")


def _ipca_do_banco(db_path: Path) -> KpiData:
    try:
        with sqlite3.connect(db_path) as conn:
            tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "ipca" not in tabelas:
                return _indisponivel("Tabela ipca ausente no banco")

            colunas = [linha[1] for linha in conn.execute("PRAGMA table_info(ipca)")]
            coluna_data = _escolher_coluna_data(colunas)
            coluna_valor = _escolher_coluna_por_chaves(
                colunas,
                ("valor", "ipca", "indice", "numero_indice"),
                excluir=(coluna_data,),
            )
            if coluna_valor is None:
                return _indisponivel("Coluna de valor do IPCA ausente")

            if coluna_data:
                query = (
                    f'SELECT "{coluna_data}", "{coluna_valor}" FROM ipca '
                    f'WHERE "{coluna_valor}" IS NOT NULL ORDER BY date("{coluna_data}") DESC LIMIT 2'
                )
                linhas = conn.execute(query).fetchall()
                atual = _converter_numero(linhas[0][1]) if linhas else None
                anterior = _converter_numero(linhas[1][1]) if len(linhas) > 1 else None
            else:
                query = (
                    f'SELECT "{coluna_valor}" FROM ipca '
                    f'WHERE "{coluna_valor}" IS NOT NULL ORDER BY rowid DESC LIMIT 2'
                )
                linhas = conn.execute(query).fetchall()
                atual = _converter_numero(linhas[0][0]) if linhas else None
                anterior = _converter_numero(linhas[1][0]) if len(linhas) > 1 else None

            if atual is None:
                return _indisponivel("Ultimo valor de IPCA invalido")

            return KpiData(
                valor=_formatar_percentual(atual),
                delta=_formatar_delta((atual - anterior) if anterior is not None else None, sufixo=" p.p."),
                fonte=f"{db_path.name}:ipca.{coluna_valor}",
                disponivel=True,
                microtexto="Variação mensal em relação ao mês anterior.",
            )
    except sqlite3.Error:
        return _indisponivel("Erro ao ler banco de macroeconomia")


def _ipca_do_csv_tabular(csv_path: Path) -> KpiData:
    try:
        linhas = _ler_csv_dict(csv_path)
        if not linhas:
            return _indisponivel("CSV de IPCA vazio")

        colunas = list(linhas[0].keys())
        coluna_data = _escolher_coluna_data(colunas)
        coluna_valor = _escolher_coluna_por_chaves(
            colunas,
            ("valor", "ipca", "indice", "numero_indice"),
            excluir=(coluna_data,),
        )
        if coluna_valor is None:
            return _indisponivel("Coluna de valor do IPCA ausente")

        serie = _extrair_serie(linhas, coluna_valor, coluna_data)
        if not serie:
            return _indisponivel("CSV de IPCA sem valores validos")

        atual = serie[-1][1]
        anterior = serie[-2][1] if len(serie) > 1 else None
        return KpiData(
            valor=_formatar_percentual(atual),
            delta=_formatar_delta((atual - anterior) if anterior is not None else None, sufixo=" p.p."),
            fonte=f"{csv_path.name}:{coluna_valor}",
            disponivel=True,
            microtexto="Variação mensal em relação ao mês anterior.",
        )
    except (OSError, csv.Error):
        return _indisponivel("Erro ao ler CSV de IPCA")


def _rentabilidade_do_comparativo(csv_path: Path) -> KpiData:
    try:
        linhas = _ler_csv_dict(csv_path)
        if not linhas:
            return _indisponivel("CSV comparativo vazio")

        colunas = list(linhas[0].keys())
        coluna_data = _escolher_coluna_data(colunas)
        coluna_carteira = _escolher_coluna_por_chaves(
            colunas,
            ("carteira_buy_and_hold", "carteira", "portfolio"),
            excluir=(coluna_data,),
        )
        coluna_ibov = _escolher_coluna_por_chaves(colunas, ("ibov", "ibovespa"), excluir=(coluna_data,))

        if coluna_carteira is None:
            return _indisponivel("Coluna da carteira ausente no comparativo")

        serie_carteira = _extrair_serie(linhas, coluna_carteira, coluna_data)
        if not serie_carteira:
            return _indisponivel("Serie da carteira invalida no comparativo")

        retorno_carteira = _retorno_acumulado_percentual(serie_carteira)

        retorno_ibov = None
        if coluna_ibov is not None:
            serie_ibov = _extrair_serie(linhas, coluna_ibov, coluna_data)
            if serie_ibov:
                retorno_ibov = _retorno_acumulado_percentual(serie_ibov)

        delta_vs_ibov = (
            _formatar_delta(retorno_carteira - retorno_ibov, sufixo=" p.p.")
            if retorno_ibov is not None
            else None
        )

        return KpiData(
            valor=_formatar_percentual(retorno_carteira),
            delta=delta_vs_ibov,
            fonte=(
                f"{csv_path.name}:{coluna_carteira} vs {coluna_ibov}"
                if coluna_ibov is not None
                else f"{csv_path.name}:{coluna_carteira}"
            ),
            disponivel=True,
            microtexto=(
                "Diferença da rentabilidade acumulada da carteira frente ao IBOV."
                if retorno_ibov is not None
                else "Retorno acumulado da carteira no período disponível."
            ),
        )
    except (OSError, csv.Error):
        return _indisponivel("Erro ao ler CSV comparativo")


def _escolher_tabela_coluna_inadimplencia(conn: sqlite3.Connection) -> tuple[str | None, str | None]:
    tabelas = [linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for tabela in tabelas:
        colunas = [linha[1] for linha in conn.execute(f'PRAGMA table_info("{tabela}")')]
        if "SeriousDlqin2yrs" in colunas:
            return tabela, "SeriousDlqin2yrs"

    for tabela in tabelas:
        colunas = [linha[1] for linha in conn.execute(f'PRAGMA table_info("{tabela}")')]
        for coluna in colunas:
            nome = _normalizar(coluna)
            if "inadimpl" in nome or "delinq" in nome:
                return tabela, coluna

    return None, None


def _inadimplencia_baixo_risco(conn: sqlite3.Connection) -> float | None:
    tabelas = {linha[0] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "credito_score" not in tabelas:
        return None

    colunas = {linha[1] for linha in conn.execute('PRAGMA table_info("credito_score")')}
    if "SeriousDlqin2yrs" not in colunas or "classificacao_risco" not in colunas:
        return None

    query = (
        "SELECT AVG(CAST(SeriousDlqin2yrs AS REAL)) "
        "FROM credito_score "
        "WHERE lower(trim(classificacao_risco)) = 'baixo risco' AND SeriousDlqin2yrs IS NOT NULL"
    )
    media = conn.execute(query).fetchone()[0]
    if media is None:
        return None
    return _to_percent(float(media))


def _escolher_coluna_data(colunas: list[str]) -> str | None:
    for coluna in colunas:
        nome = _normalizar(coluna)
        if nome in {"data", "date", "mes", "periodo", "timestamp"}:
            return coluna
    for coluna in colunas:
        nome = _normalizar(coluna)
        if "data" in nome or "date" in nome or "periodo" in nome:
            return coluna
    return None


def _escolher_coluna_por_chaves(
    colunas: list[str],
    chaves: tuple[str, ...],
    excluir: tuple[str | None, ...] = (),
) -> str | None:
    excluidas = {item for item in excluir if item}
    candidatos = [c for c in colunas if c not in excluidas]
    for chave in chaves:
        chave_norm = _normalizar(chave)
        for coluna in candidatos:
            if chave_norm in _normalizar(coluna):
                return coluna
    return candidatos[0] if candidatos else None


def _extrair_serie(
    linhas: list[dict[str, str]],
    coluna_valor: str,
    coluna_data: str | None,
) -> list[tuple[date | None, float]]:
    serie: list[tuple[date | None, float]] = []
    for linha in linhas:
        valor = _converter_numero(linha.get(coluna_valor))
        if valor is None:
            continue
        data_val = _parse_data_flex(linha.get(coluna_data)) if coluna_data else None
        serie.append((data_val, valor))

    if coluna_data:
        serie.sort(key=lambda item: (item[0] is None, item[0] or date.min))
    return serie


def _retorno_acumulado_percentual(serie: list[tuple[date | None, float]]) -> float:
    primeiro = serie[0][1]
    ultimo = serie[-1][1]
    if 95 <= primeiro <= 105:
        return ((ultimo / 100) - 1) * 100
    if 0.95 <= primeiro <= 1.05:
        return (ultimo - 1) * 100
    if -0.1 <= primeiro <= 0.1 and -1 <= ultimo <= 1:
        return ultimo * 100
    return ultimo


def _to_percent(valor: float) -> float:
    return valor * 100 if valor <= 1.5 else valor


def _ler_csv_dict(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        amostra = arquivo.read(4096)
        arquivo.seek(0)
        delimitador = ";" if amostra.count(";") > amostra.count(",") else ","
        leitor = csv.DictReader(arquivo, delimiter=delimitador)
        return [linha for linha in leitor if linha]


def _converter_numero(valor: object) -> float | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    texto = texto.replace("%", "").replace(" ", "")
    texto = texto.replace(".", "").replace(",", ".") if "," in texto and "." in texto else texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def _parse_data_flex(valor: object) -> date | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    formatos = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m", "%Y/%m", "%m/%Y")
    for formato in formatos:
        try:
            data = datetime.strptime(texto, formato)
            return date(data.year, data.month, 1)
        except ValueError:
            continue
    return None


def _formatar_percentual(valor: float) -> str:
    return f"{valor:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_delta(valor: float | None, sufixo: str = "%") -> str | None:
    if valor is None:
        return None
    sinal = "+" if valor >= 0 else ""
    numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{numero}{sufixo}"


def _normalizar(texto: object) -> str:
    texto_limpo = str(texto or "").strip().lower()
    sem_acentos = unicodedata.normalize("NFKD", texto_limpo).encode("ascii", "ignore").decode("ascii")
    return sem_acentos


def _indisponivel(fonte: str) -> KpiData:
    return KpiData(
        valor="Indisponível",
        delta=None,
        fonte=fonte,
        disponivel=False,
        microtexto="Dado indisponível para o recorte atual.",
    )
