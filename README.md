# Dashboard Econômico
> Portfólio de análise de dados financeiros | Python · Streamlit · SQL

## 🔗 Acesse o Dashboard

[Visualizar aplicação online](https://caio-dashboard-economico.streamlit.app)


Este projeto organiza, em um único dashboard, três frentes que costumam ser analisadas separadamente: **macroeconomia, crédito e investimentos**.

Na prática, ele resolve um problema simples: transformar dados financeiros de fontes diferentes em uma leitura clara, comparável e fácil de apresentar, sem perder cuidado metodológico.

## Motivação

Eu criei este dashboard para reunir em um só lugar análises que já fazia em projetos separados.

A ideia foi construir um projeto de portfólio que mostrasse, de forma objetiva:
- leitura de cenário com IPCA e Selic;
- segmentação de risco de crédito com score explicável;
- comparação de performance de carteira buy and hold contra benchmarks.

## Tecnologias usadas

- **Python**
- **Streamlit** (aplicação web e navegação multipágina)
- **Pandas** (tratamento e modelagem tabular)
- **Matplotlib** (gráficos analíticos)
- **Plotly** (uso complementar em visualizações)
- **SQLite** (persistência local para macroeconomia e crédito)

Dependências principais (arquivo `requirements.txt`):
- `streamlit>=1.36,<2.0`
- `pandas>=2.2,<3.0`
- `matplotlib>=3.8,<4.0`
- `plotly>=5.22,<6.0`

## Como rodar localmente

1. Clone ou baixe o projeto.
2. No terminal, acesse a pasta raiz:

```powershell
cd dashboard-economico
```

3. (Opcional, recomendado) Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Instale as dependências:

```powershell
pip install -r requirements.txt
```

5. Execute o app:

```powershell
python -m streamlit run app.py
```

## Estrutura de arquivos

```text
dashboard-economico/
|-- app.py
|-- requirements.txt
|-- README.md
|-- assets/
|   `-- perfil.jpg
|-- pages/
|   |-- macroeconomia.py
|   |-- credito.py
|   |-- investimentos.py
|   `-- sobre.py
|-- utils/
|   |-- __init__.py
|   `-- kpis.py
`-- dados/
    |-- macroeconomia/
    |   |-- dados_economicos.db
    |   `-- ipca.csv
    |-- credito/
    |   `-- risco_credito.db
    `-- investimentos/
        |-- comparativo_carteira_benchmarks.csv
        `-- carteira_consolidada.csv
```

## O que o dashboard entrega

### 1) Macroeconomia
- Série histórica de **IPCA e Selic** (2015-2024).
- Gráfico de **IPCA acumulado em 12 meses** com linha de referência visual de 3,0%.
- Resumo lateral com leitura descritiva e cautela metodológica (sem inferência causal forte).

### 2) Crédito
- Inadimplência média por faixa de risco (baixo, médio e alto risco).
- Distribuição real do score na base.
- Destaque para diferença de inadimplência entre extremos de risco.

### 3) Investimentos
- Evolução histórica de carteira hipotética versus **IBOV** e **CDI (proxy)**.
- Retorno anual com indicação de ano corrente parcial (YTD).
- Métricas de risco e retorno: drawdown, volatilidade e relação retorno/volatilidade (`rf=0`).

### 4) Sobre
- Contexto profissional, certificações (CPA-10 e CPA-20), stack técnica e links.
- Bloco de experiência com resultados quantitativos para portfólio.

## Principais conclusões analíticas

- IPCA e Selic apresentam associação com defasagem temporal visível na série 2015-2024.
- Inadimplência é significativamente maior nas faixas de alto risco; a segmentação por score evidencia forte heterogeneidade.
- Carteira hipotética supera IBOV e CDI no período analisado, com análise complementar por volatilidade e drawdown.

## Fontes de dados

- **Banco Central (SGS)**: séries macroeconômicas (IPCA e Selic).
- **Give Me Some Credit (Kaggle)**: base para análise de risco de crédito.
- **Séries tratadas no pipeline do projeto**: carteira hipotética buy and hold e benchmarks (IBOV e CDI proxy) usados nas comparações.
