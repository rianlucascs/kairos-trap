

from streamlit_apps.apps.streamlit_app_research.application.analytics.price_regression_analysis import PriceRegressionAnalysis

import streamlit as st
import plotly.graph_objects as go        


def render_price_regression_chart(
    analysis: PriceRegressionAnalysis,
) -> None:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=analysis.data["Date"],
            y=analysis.distance_pct,
            mode="lines",
            name="Distância",
        )
    )

    fig.add_hline(
        y=0,
        line_color="purple",
        line_width=2,
    )

    fig.add_hline(
        y=analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_hline(
        y=-analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_hline(
        y=2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.add_hline(
        y=-2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Distância da Tendência (%)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(fig, width="stretch")
    

def render_price_regression_distribution_chart(
    analysis: PriceRegressionAnalysis,
) -> None:

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=analysis.distance_pct,
            nbinsx=60,
        )
    )

    fig.add_vline(
        x=analysis.current,
        line_color="red",
        line_width=2,
        annotation_text="Atual",
        annotation_position="top",
    )

    fig.add_vline(
        x=analysis.mean,
        line_color="purple",
        line_width=2,
        annotation_text="Média",
        annotation_position="top",
    )

    fig.add_vline(
        x=analysis.mean + analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_vline(
        x=analysis.mean - analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_vline(
        x=analysis.mean + 2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.add_vline(
        x=analysis.mean - 2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.update_layout(
        xaxis_title="Distância da Tendência (%)",
        yaxis_title="Frequência",
        xaxis=dict(ticksuffix="%"),
        bargap=0.05,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(fig, width="stretch")