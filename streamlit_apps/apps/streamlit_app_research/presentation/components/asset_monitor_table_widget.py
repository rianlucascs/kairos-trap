

import pandas as pd
import streamlit as st


def render_asset_monitor_table_widget(
    data: dict # asset_monitoring.get_stats_by_ticker()
) -> None:
    
    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.reset_index().rename(columns={"index": "ativo"})
    df["date_last_price"] = pd.to_datetime(df["date_last_price"]).dt.date
    df = df.sort_values("current_drawdown%")

    pct_cols = ["current_distance_media20%", "current_distance_regression%", "current_drawdown%"]

    styled = (
        df.style
        .format({col: "{:.1f}%" for col in pct_cols} | {"last_price": "R$ {:.2f}"})
        .background_gradient(cmap="RdYlGn", subset=pct_cols, vmin=-30, vmax=30)
    )

    row_height = 35
    header_height = 38
    table_height = header_height + row_height * len(df)

    st.dataframe(styled, hide_index=True, width="stretch", height=table_height)