

import streamlit as st
import plotly.graph_objects as go
from pandas import DataFrame
import numpy as np


def _optimal_nbins(returns) -> int:
    n = len(returns)
    if n < 2:
        return 1

    q75, q25 = np.percentile(returns, [75, 25])
    iqr = q75 - q25

    if iqr == 0:
        return 30  # fallback quando a distribuição é muito concentrada

    bin_width = 2 * iqr * (n ** (-1 / 3))
    data_range = returns.max() - returns.min()

    return max(1, int(np.ceil(data_range / bin_width)))


def render_returns_distribution_bar_chart(
    data: DataFrame,
    moving_average: int | None = None,
    _xaxis_title: str = "Retorno Diário",
    _yaxis_title: str = "Frequência",
) -> None:
    
    returns = data[[c for c in data.columns if "returns" in c][0]].dropna()

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
            nbinsx=_optimal_nbins(returns),
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
        xaxis_title=_xaxis_title,
        yaxis_title=_yaxis_title,
        xaxis=dict(tickformat=".1%"),
        bargap=0.05,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )