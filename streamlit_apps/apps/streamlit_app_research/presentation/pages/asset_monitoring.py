

# --- Libraries ---


from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import AssetScreeningUnsupervisedLearning_1, get_eligible_assets_unsupervised_learning_1
from streamlit_apps.apps.streamlit_app_research.presentation.components.asset_monitor_table_widget import render_asset_monitor_table_widget
from streamlit_apps.apps.streamlit_app_research.application.services.asset_monitoring import AssetMonitoring

import streamlit as st


# --- Service Initialization ---


result: dict = get_eligible_assets_unsupervised_learning_1(service=AssetScreeningUnsupervisedLearning_1())
asset_monitoring = AssetMonitoring(
    result=result,
    cluster=3
)


# --- Asset Monitoring ---


st.title("Asset Monitoring")
st.subheader("Ativos do Cluster 3 — Unsupervised Learning 1")
      
render_asset_monitor_table_widget(asset_monitoring.get_stats_by_ticker())