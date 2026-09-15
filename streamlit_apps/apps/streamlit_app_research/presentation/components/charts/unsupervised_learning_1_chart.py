from collections.abc import Sequence

import plotly.express as px
import streamlit as st
from pandas import DataFrame
from sklearn.decomposition import PCA


def render_unsupervised_learning_1_chart(
    data: DataFrame,
    X_scaled,
    ativo_destaque: str = "KLBN11",
) -> None:
    """Renderiza os clusters de ativos em uma projeção PCA bidimensional."""

    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(X_scaled)

    chart_data = data.copy()
    chart_data["pca_1"] = components[:, 0]
    chart_data["pca_2"] = components[:, 1]
    chart_data["cluster"] = chart_data["cluster"].astype(str)

    hover_data = _get_hover_data(chart_data)
    explained_variance = pca.explained_variance_ratio_

    fig = px.scatter(
        chart_data,
        x="pca_1",
        y="pca_2",
        color="cluster",
        hover_name="cod",
        hover_data=hover_data,
        labels={
            "pca_1": f"PC1 ({explained_variance[0]:.1%} var.)",
            "pca_2": f"PC2 ({explained_variance[1]:.1%} var.)",
            "cluster": "Cluster",
        },
        title="Clusters de ativos - projeção PCA 2D",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )

    ativo = chart_data[chart_data["cod"] == ativo_destaque]

    if not ativo.empty:
        fig.add_scatter(
            x=ativo["pca_1"],
            y=ativo["pca_2"],
            mode="markers+text",
            text=ativo["cod"],
            textposition="top center",
            marker=dict(
                size=14,
                color="#D4AF37",
                symbol="diamond",
                line=dict(width=1, color="black"),
            ),
            name=f"Ativo: {ativo_destaque}",
        )

    fig.update_traces(
        marker=dict(size=12, line=dict(width=0.5, color="white")),
        selector=dict(mode="markers"),
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)

    fig.update_layout(
        legend_title_text="Cluster",
        hoverlabel=dict(bgcolor="#2D2D2D", font_size=13),
        height=550,
    )

    st.plotly_chart(fig, width="stretch")


def _get_hover_data(data: DataFrame) -> dict[str, bool | str]:
    formats = {
        "asset": True,
        "media_ret": ":.4f",
        "std_ret": ":.4f",
        "ma_volume_financeiro": ":.2e",
        "std_volume_financeiro": ":.2e",
        "media_lucro_liquido": ":.2e",
        "std_lucro_liquido": ":.2e",
        "media_divida_liquida": ":.2e",
        "std_divida_liquida": ":.2e",
        "mediana_divida_liquida": ":.2e",
        "pca_1": False,
        "pca_2": False,
    }

    return {
        column: format_value
        for column, format_value in formats.items()
        if column in data.columns
    }