

import streamlit as st


def render_moving_average_select_widget(key, options: list = [None, 20, 10, 5, 50, 100, 200]):
    
    return st.selectbox(
        "Média móvel",
        options=options,
        format_func=lambda value: (
            "Nenhuma" if value is None else f"{value} períodos"
        ),
        key=key,
    )