from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]


def _encontrar_foto_perfil() -> Path | None:
    """Procura uma imagem de perfil em locais comuns do projeto."""
    candidatos = [
        BASE_DIR / "assets" / "perfil.jpg",
        BASE_DIR / "assets" / "perfil.png",
        BASE_DIR / "foto.jpg",
        BASE_DIR / "foto.png",
    ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None


st.markdown(
    """
    <style>
    .sobre-titulo {
        color: #1f3b5c;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.9rem 0;
        letter-spacing: -0.4px;
    }
    .sobre-nome {
        color: #1f2937;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.8rem 0;
        letter-spacing: -0.3px;
    }
    .sobre-subtitulo {
        color: #1f3b5c;
        font-size: 1.05rem;
        font-weight: 600;
        margin: 1rem 0 0.4rem 0;
    }
    [data-testid="stImage"] img {
        border-radius: 12px;
        border: 1px solid #d9e0e7;
    }
    .sobre-paragrafo {
        margin-bottom: 0.85rem;
        line-height: 1.58;
        color: #334155;
    }
    .sobre-links {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.3rem;
    }
    .sobre-link {
        display: inline-block;
        padding: 0.4rem 0.7rem;
        border: 1px solid #d9e0e7;
        border-radius: 8px;
        color: #1f3b5c;
        text-decoration: none;
        font-weight: 600;
        background: #f8fafc;
    }
    .sobre-link:hover {
        background: #eef3f8;
    }
    .sobre-certificacoes {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.2rem 0 0.5rem 0;
    }
    .sobre-certificacao {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border: 1px solid #cbd5e1;
        border-radius: 999px;
        color: #1f3b5c;
        background: #f1f5f9;
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 class='sobre-titulo'>Sobre</h1>", unsafe_allow_html=True)

col_esquerda, col_direita = st.columns([1, 2.2], gap="large")

with col_esquerda:
    foto = _encontrar_foto_perfil()
    if foto is not None:
        st.image(str(foto), width=220)
    else:
        st.markdown("&nbsp;", unsafe_allow_html=True)

with col_direita:
    st.markdown("<h2 class='sobre-nome'>Caio César Merzbacher</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sobre-paragrafo'>"
        "Estudante de Ciências Econômicas na USCS, com experiência prática em rotinas fiscais e tributárias "
        "e automação de processos com Python."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sobre-paragrafo'>"
        "Atuo na interseção entre economia, finanças e dados, com projetos aplicados em macroeconomia, "
        "risco de crédito e investimentos."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<p class='sobre-subtitulo'>Certificações</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sobre-certificacoes">
            <span class="sobre-certificacao">CPA-10</span>
            <span class="sobre-certificacao">CPA-20</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p class='sobre-subtitulo'>Stack técnica</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sobre-links">
            <span class="sobre-link">Python</span>
            <span class="sobre-link">Pandas</span>
            <span class="sobre-link">Streamlit</span>
            <span class="sobre-link">SQLite</span>
            <span class="sobre-link">Plotly</span>
            <span class="sobre-link">Matplotlib</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p class='sobre-subtitulo'>Experiência e projetos</p>", unsafe_allow_html=True)
    st.markdown("- Modelo de scoring aplicado a base com cerca de 150 mil registros, com inadimplência 12,9x maior entre classes extremas de risco.")
    st.markdown("- Carteira hipotética buy and hold com retorno acumulado de +170,44%, acima de CDI e IBOV no período analisado.")
    st.markdown("- Análise de séries históricas de IPCA e Selic (2015–2024) com dados do Banco Central (SGS).")
    st.markdown("- 2 anos de atuação como Auxiliar Fiscal, com automação de rotinas tributárias em Python.")
    st.markdown("<p class='sobre-subtitulo'>Links</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sobre-links">
            <a class="sobre-link" href="https://github.com/CaioMerz" target="_blank">GitHub</a>
            <a class="sobre-link" href="https://www.linkedin.com/in/caio-c%C3%A9sar-merzbacher-252565264/" target="_blank">LinkedIn</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
