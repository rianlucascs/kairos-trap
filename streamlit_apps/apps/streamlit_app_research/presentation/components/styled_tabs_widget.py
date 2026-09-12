

import streamlit as st


# Seletores validados contra Streamlit 1.63.0.
# Streamlit migrou o componente de tabs para uma base diferente (react-aria)

_TABS_CSS = """
<style>
div[data-testid="stTabs"] [role="tablist"] {
    gap: 8px;
}

div[data-testid="stTab"] {
    padding: 10px 28px !important;
    border-radius: 1px !important;
    background-color: #2D2D2D !important;
}

div[data-testid="stTab"] p {
    color: #FFFFFF !important;
    font-weight: 400 !important;
}

div[data-testid="stTab"][aria-selected="true"] {
    background-color: #E8752C !important;
}

div[data-testid="stTab"][aria-selected="true"] p {
    color: black !important;
    font-weight: 700 !important;
}

div[data-testid="stTab"] .react-aria-SelectionIndicator {
    background-color: transparent !important;
}
</style>
"""


def styled_tabs_widget(labels: list[str]) -> list:
    """Cria st.tabs com o estilo pill (Excel-dark) já aplicado.

    Uso:
        tab1, tab2 = styled_tabs(["Visão Geral", "Detalhamento"])
        with tab1:
            ...
    """

    st.markdown(_TABS_CSS, unsafe_allow_html=True)

    return st.tabs(labels)