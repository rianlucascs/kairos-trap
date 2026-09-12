

import streamlit as st
from pandas import DataFrame, to_datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def render_price_line_chart(price: DataFrame) -> None:
    
    
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.15,
        subplot_titles=("Preço ajustado", "Volume"),
    )

    # Preço
    fig.add_trace(
        go.Scatter(
            x=price["Date"],
            y=price["Adj Close"],
            mode="lines",
            # line=dict(
            #     color="#3B82F6",
            #     width=2,
            # ),
            name="Preço ajustado",
            hovertemplate="R$ %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Volume
    fig.add_trace(
        go.Bar(
            x=price["Date"],
            y=price["Volume"],
            width=86_400_000 * 0.5,  # 80% de 1 dia em ms
            marker_color="#7F848D",
            name="Volume",
            hovertemplate="%{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Dias sem negociação (Volume = 0) não geram barra visível; marca-los explicitamente evita a impressão de dado ausente.
    zero_volume = price[price["Volume"] == 0]
    if not zero_volume.empty:
        fig.add_trace(
            go.Scatter(
                x=zero_volume["Date"],
                y=[0] * len(zero_volume),
                mode="markers",
                marker=dict(color="#EF4444", size=4, symbol="line-ns", line=dict(width=2, color="#EF4444")),
                name="Sem negociação",
                hovertemplate="Sem negociação<extra></extra>",
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=dict(
            text="Histórico de Preço e Volume",
            x=0,
            xanchor="left",
            font=dict(size=18),
        ),
        # template="plotly_dark",
        height=550,
        showlegend=False,
        margin=dict(
            l=60,
            r=30,
            t=70,
            b=40,
        ),
    )

    # Eixo Y — preço
    fig.update_yaxes(
        title_text="Preço (R$)",
        tickprefix="R$ ",
        tickformat=".2f",
        row=1,
        col=1,
    )

    # Eixo Y — volume
    fig.update_yaxes(
        title_text="Volume",
        tickformat="~s",
        row=2,
        col=1,
    )

    # Eixo X
    fig.update_xaxes(
        title_text="Data",
        showgrid=False,
        row=2,
        col=1,
    )

    # Grid mais discreto
    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )