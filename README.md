# Dashboard EconÃ´mico
> PortfÃ³lio de anÃ¡lise de dados financeiros | Python Â· Streamlit Â· SQL

## 🔗 Acesse o Dashboard

[Visualizar aplicação online](https://caio-dashboard-economico.streamlit.app)


Este projeto organiza, em um Ãºnico dashboard, trÃªs frentes que costumam ser analisadas separadamente: **macroeconomia, crÃ©dito e investimentos**.

Na prÃ¡tica, ele resolve um problema simples: transformar dados financeiros de fontes diferentes em uma leitura clara, comparÃ¡vel e fÃ¡cil de apresentar, sem perder cuidado metodolÃ³gico.

## MotivaÃ§Ã£o

Eu criei este dashboard para reunir em um sÃ³ lugar anÃ¡lises que jÃ¡ fazia em projetos separados.

A ideia foi construir um projeto de portfÃ³lio que mostrasse, de forma objetiva:
- leitura de cenÃ¡rio com IPCA e Selic;
- segmentaÃ§Ã£o de risco de crÃ©dito com score explicÃ¡vel;
- comparaÃ§Ã£o de performance de carteira buy and hold contra benchmarks.

## Tecnologias usadas

- **Python**
- **Streamlit** (aplicaÃ§Ã£o web e navegaÃ§Ã£o multipÃ¡gina)
- **Pandas** (tratamento e modelagem tabular)
- **Matplotlib** (grÃ¡ficos analÃ­ticos)
- **Plotly** (uso complementar em visualizaÃ§Ãµes)
- **SQLite** (persistÃªncia local para macroeconomia e crÃ©dito)

DependÃªncias principais (arquivo `requirements.txt`):
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

4. Instale as dependÃªncias:

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
- SÃ©rie histÃ³rica de **IPCA e Selic** (2015-2024).
- GrÃ¡fico de **IPCA acumulado em 12 meses** com linha de referÃªncia visual de 3,0%.
- Resumo lateral com leitura descritiva e cautela metodolÃ³gica (sem inferÃªncia causal forte).

### 2) CrÃ©dito
- InadimplÃªncia mÃ©dia por faixa de risco (baixo, mÃ©dio e alto risco).
- DistribuiÃ§Ã£o real do score na base.
- Destaque para diferenÃ§a de inadimplÃªncia entre extremos de risco.

### 3) Investimentos
- EvoluÃ§Ã£o histÃ³rica de carteira hipotÃ©tica versus **IBOV** e **CDI (proxy)**.
- Retorno anual com indicaÃ§Ã£o de ano corrente parcial (YTD).
- MÃ©tricas de risco e retorno: drawdown, volatilidade e relaÃ§Ã£o retorno/volatilidade (`rf=0`).

### 4) Sobre
- Contexto profissional, certificaÃ§Ãµes (CPA-10 e CPA-20), stack tÃ©cnica e links.
- Bloco de experiÃªncia com resultados quantitativos para portfÃ³lio.

## Principais conclusÃµes analÃ­ticas

- IPCA e Selic apresentam associaÃ§Ã£o com defasagem temporal visÃ­vel na sÃ©rie 2015-2024.
- InadimplÃªncia Ã© significativamente maior nas faixas de alto risco; a segmentaÃ§Ã£o por score evidencia forte heterogeneidade.
- Carteira hipotÃ©tica supera IBOV e CDI no perÃ­odo analisado, com anÃ¡lise complementar por volatilidade e drawdown.

## Fontes de dados

- **Banco Central (SGS)**: sÃ©ries macroeconÃ´micas (IPCA e Selic).
- **Give Me Some Credit (Kaggle)**: base para anÃ¡lise de risco de crÃ©dito.
- **SÃ©ries tratadas no pipeline do projeto**: carteira hipotÃ©tica buy and hold e benchmarks (IBOV e CDI proxy) usados nas comparaÃ§Ãµes.
