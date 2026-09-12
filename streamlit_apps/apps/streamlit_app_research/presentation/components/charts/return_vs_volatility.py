

from streamlit_apps.apps.streamlit_app_research.application.analytics.return_volatility_analysis import ReturnVolatilityAnalysis

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_return_vs_volatility_chart(
    analysis: ReturnVolatilityAnalysis,
) -> None:

    data = analysis.data

    fig = go.Figure()

    # Observações
    fig.add_trace(
        go.Scatter(
            x=data["volatility"],
            y=data["mean_return"],
            mode="markers",
            name="Observações",
            marker=dict(
                size=6,
                opacity=0.5,
            ),
        )
    )

    lookbacks = [0, 2, 3]
    labels = ["Atual", "Anterior", "Anterior 2"]

    vols = [analysis.current_volatility(lookback=lb) if lb else analysis.current_volatility() for lb in lookbacks]
    rets = [analysis.current_return(lookback=lb) if lb else analysis.current_return() for lb in lookbacks]

    # Pontos de interesse: Atual, Anterior, Anterior 2
    fig.add_trace(
        go.Scatter(
            x=vols,
            y=rets,
            mode="markers+lines",
            text=labels,
            textposition="top center",
            line=dict(color="orange", width=3, dash="dot"),
            marker=dict(
                size=[14, 10, 7],           # decrescente = recência
                color="orange",
                symbol="diamond",
                opacity=[1.0, 0.6, 0.35],    # decrescente = recência
                line=dict(color="purple", width=0.77),
            ),
            showlegend=False,
            hovertext=labels,
            hoverinfo="text+x+y",
        )
    )

    # Elipse
    fig.add_trace(
        go.Scatter(
            x=analysis.ellipse_x,
            y=analysis.ellipse_y,
            mode="lines",
            name="Dispersão",
            line=dict(
                color="red",
                width=1,
            ),
        )
    )

    # Regressão
    coef = np.polyfit(
        data["volatility"],
        data["mean_return"],
        1,
    )

    x_line = np.linspace(
        data["volatility"].min(),
        data["volatility"].max(),
        100,
    )

    y_line = coef[0] * x_line + coef[1]

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Regressão",
            line=dict(
                color="purple",
                width=1,
                dash="dash",
            ),
        )
    )

    # Média de volatilidade
    fig.add_vline(
        x=analysis.mean_volatility,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    # Média de retorno
    fig.add_hline(
        y=analysis.mean_return,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    # R²
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"R² = {analysis.r2:.2f}",
        showarrow=False,
    )

    fig.update_layout(
        xaxis_title="Volatilidade",
        yaxis_title="Retorno Médio",
        xaxis=dict(
            tickformat=".1%",
        ),
        yaxis=dict(
            tickformat=".1%",
        ),
        hovermode="closest",
        showlegend=True,
        margin=dict(
            l=0,
            r=0,
            t=30,
            b=0,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )