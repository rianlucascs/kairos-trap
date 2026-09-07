

import streamlit as st
from pandas import DataFrame


def render_information_table_widget(
    data: dict[str, str],
    title: str | None = None,
) -> None:

    df = DataFrame(
        data.items(),
        columns=["Informação", "Valor"],
    ).set_index("Informação")
    
    if title is not None:

        st.subheader(title)
        
    st.table(
        df,
        width="stretch",
    )