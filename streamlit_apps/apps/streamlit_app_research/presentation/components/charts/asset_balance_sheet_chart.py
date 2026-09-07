

import streamlit as st
import plotly.graph_objects as go
from pandas import DataFrame
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ChartSeries:
    df: DataFrame
    x: str
    y: str
    name: str


def render_asset_balance_sheet_chart(
    series: list[ChartSeries],
    title: str,
    xlabel: str | None = None,
    ylabel: str | None = None,
    chart_type: Literal["line", "bar"] = "line",
) -> None:

    fig = go.Figure()

    for s in series:

        if chart_type == "line":
            fig.add_trace(
                go.Scatter(
                    x=s.df[s.x],
                    y=s.df[s.y],
                    mode="lines",
                    name=s.name,
                )
            )

        elif chart_type == "bar":
            fig.add_trace(
                go.Bar(
                    x=s.df[s.x],
                    y=s.df[s.y],
                    name=s.name,
                )
            )

    fig.update_layout(
        title=dict(
            text=title,
            x=0,
            xanchor="left",
        ),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )
