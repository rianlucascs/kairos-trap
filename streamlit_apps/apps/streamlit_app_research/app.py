


import streamlit as st


st.set_page_config(
    page_title="kairos-trap",
    page_icon="\U0001FA99",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("presentation/pages/asset_explorer.py", title="Asset Explorer"),
        st.Page("presentation/pages/market_overview.py", title="Market Overview"),
    ]
)

pg.run()

with st.sidebar:
    
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="font-size: 24px; font-weight: bold;">Financial Research</h1>
            <p style="font-size: 14px;">Exploração e análise financeira.</p>
            <p style="font-size: 12px; color: gray;">
                Built by <a href="https://github.com/rianlucascs" target="_blank">@rianlucascs</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )