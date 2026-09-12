

import streamlit as st
import plotly.graph_objects as go
from pandas import DataFrame


def render_returns_distribution_bar_chart(
    daily_returns: DataFrame,
    moving_average: int | None = None,
) -> None:
    
    returns = daily_returns["daily_returns"].dropna()

    if moving_average:
        returns = returns.rolling(moving_average).mean().dropna()

    mean = returns.mean()
    std = returns.std()

    current_return = returns.iloc[-1]

    upper_1std = mean + std
    lower_1std = mean - std

    upper_2std = mean + (2 * std)
    lower_2std = mean - (2 * std)

    fig = go.Figure(
        go.Histogram(
            x=returns,
            nbinsx=60,
        )
    )

    # Retorno atual
    fig.add_vline(
        x=current_return,
        line_color="red",
        line_width=2,
        annotation_text="Atual",
        annotation_position="top",
    )

    # Média
    fig.add_vline(
        x=mean,
        line_color="purple",
        line_width=4,
        line_dash="solid",
        annotation_text="Média",
        annotation_position="top",
    )

    # +1σ
    fig.add_vline(
        x=upper_1std,
        line_color="lightgray",
        line_dash="dash",
        annotation_text="+1σ",
        annotation_position="top",
    )

    # -1σ
    fig.add_vline(
        x=lower_1std,
        line_color="lightgray",
        line_dash="dash",
        annotation_text="-1σ",
        annotation_position="top",
    )

    # +2σ
    fig.add_vline(
        x=upper_2std,
        line_color="lightgray",
        line_dash="dot",
        annotation_text="+2σ",
        annotation_position="top",
    )

    # -2σ
    fig.add_vline(
        x=lower_2std,
        line_color="lightgray",
        line_dash="dot",
        annotation_text="-2σ",
        annotation_position="top",
    )

    fig.update_layout(
        xaxis_title="Retorno Diário",
        yaxis_title="Frequência",
        xaxis=dict(tickformat=".1%"),
        bargap=0.05,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )