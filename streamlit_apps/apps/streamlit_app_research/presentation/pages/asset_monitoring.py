

# --- Libraries ---


from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import AssetScreeningUnsupervisedLearning_1, get_eligible_assets_unsupervised_learning_1
from streamlit_apps.apps.streamlit_app_research.application.services.asset_monitoring import AssetMonitoring
from streamlit_apps.apps.streamlit_app_research.application.services.asset_momentum_ranking_1_0_service import (
    AssetMomentumRankingService,
    get_current_momentum_ranking,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components import (
    render_asset_monitor_table_widget,
    styled_tabs_widget
)

import streamlit as st


# --- Service Initialization ---


result: dict = get_eligible_assets_unsupervised_learning_1(service=AssetScreeningUnsupervisedLearning_1())

asset_monitoring = AssetMonitoring(result=result, cluster=3)


# --- Asset Monitoring ---


st.title("Asset Monitoring")
st.subheader("Ativos do Cluster 3 — Unsupervised Learning 1")
st.info(AssetScreeningUnsupervisedLearning_1.__doc__)


# --- Asset Monitoring Tabs ---


distancias, rankings = styled_tabs_widget(["Distâncias", "Rankings"])

with distancias:
    
    render_asset_monitor_table_widget(
        data=asset_monitoring.get_stats_by_ticker(),
        percent_columns=None,
        color_columns={
            "current_distance_media20%": {"cmap": "RdYlGn", "vmin": -10.00, "vmax": 10.00},
            "current_distance_regression%": {"cmap": "RdYlGn", "vmin": -30.00, "vmax": 30.00},
            "current_drawdown%": {"cmap": "RdYlGn", "vmin": -80.00, "vmax": 80.00},
        },
        formatters={"last_price": "R$ {:.2f}"},
        date_columns=["date_last_price"],
        sort_by="current_drawdown%",
        ascending=True,
    )
    

with rankings:
    
    # research/research_studies/backtesting/... rankings/... /1, /2, /3
    
    r1, r2, r3 = styled_tabs_widget(["Ranking 1", "Ranking 2", "Ranking 3"])
    
    with r1:
        
        st.write(AssetMomentumRankingService.__doc__.replace("\n\n", "\n"))
        
        ranking_key = "asset_monitoring::ranking_1"
        load_ranking_key = "asset_monitoring::load_ranking_1"

        if ranking_key not in st.session_state:
            if st.button("Carregar ranking", key=load_ranking_key):
                try:
                    st.session_state[ranking_key] = get_current_momentum_ranking(
                        service=AssetMomentumRankingService(),
                        tickers=asset_monitoring.get_assets_by_cluster(),
                    )
                    st.rerun()
                except Exception as error:
                    st.error(f"Nao foi possivel calcular o ranking: {error}")
        else:
            ranking_result = st.session_state[ranking_key]
            if not isinstance(ranking_result, dict):
                del st.session_state[ranking_key]
                st.rerun()

            ranking = ranking_result["ranking"]
            metrics = ranking_result["metrics"]
            recommended_ticker = ranking.iloc[0]["ticker"].removesuffix(".SA")
            signal_date = ranking.iloc[0]["date"].date()

            st.success(
                f"O Ridge esta recomendando {recommended_ticker} em {signal_date:%d/%m/%Y}; "
                f"historicamente, sua escolha top-1 superou a media do universo em "
                f"{metrics['ridge_hit_rate_walk_forward']:.1%} das "
                f"{metrics['test_days']} datas fora da amostra "
                f"({metrics['folds']} folds walk-forward)."
            )
            render_asset_monitor_table_widget(
                data=ranking,
                color_columns={
                    "ridge_score": {"cmap": "RdYlGn", "vmin": -0.0010, "vmax": 0.0010},
                },
                date_columns=["date"],
                sort_by="ridge_score",
                ascending=False,
            )
