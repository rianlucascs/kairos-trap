

from streamlit_apps.apps.streamlit_app_research.presentation.components import styled_tabs_widget
from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import (
    AssetScreening10yPrice10yITRService, get_eligible_assets_10yPrice10yITR,
    AssetScreeningUnsupervisedLearning_1, get_eligible_assets_unsupervised_learning_1,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts import render_unsupervised_learning_1_chart

from typing import TypedDict
from pandas import DataFrame
import streamlit as st


def load_on_demand(key: str, loader):
    """
    Garante carregamento lazy: só executa `loader()` quando o usuário clica
    no botão, e guarda o resultado em session_state para não recalcular
    em reruns seguintes (troca de tab, outros widgets, etc.).
    Retorna o DataFrame se já carregado, ou None (e já desenha o botão/info).
    """
    if key not in st.session_state:
        if st.button("Carregar screening", key=f"load::{key}"):
            with st.spinner("Calculando..."):
                st.session_state[key] = loader()
            st.rerun()
        else:
            st.info("Clique para carregar este screening.")
        return None

    return st.session_state[key]


def render_screening_10y_price_10y_itr(tab):
    with tab:
        st.markdown(f"**Descrição:** {AssetScreening10yPrice10yITRService.__doc__}")

        df = load_on_demand(
            key="screening::10y_price_10y_itr",
            loader=lambda: get_eligible_assets_10yPrice10yITR(
                service=AssetScreening10yPrice10yITRService()
            ),
        )
        if df is None:
            return

        st.markdown("Resultados do screening:")
        st.dataframe(df)

        st.markdown("Código Python utilizado:")
        st.code(
            """
            from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import AssetScreening10yPrice10yITRService, get_eligible_assets_10yPrice10yITR
            df: DataFrame = get_eligible_assets_10yPrice10yITR(service=AssetScreening10yPrice10yITRService())
            """,
            language="python",
            line_numbers=True,
            wrap_lines=True,
        )
        

class UnsupervisedScreeningResult(TypedDict):
    df: DataFrame
    X_scaled: DataFrame
    
    
def render_screening_unsupervised_learning_1(tab):
    with tab:
        st.markdown(f"**Descrição:** {AssetScreeningUnsupervisedLearning_1.__doc__}")

        result: UnsupervisedScreeningResult | None = load_on_demand(
            key="screening::unsupervised_learning_1",
            loader=lambda: get_eligible_assets_unsupervised_learning_1(
                service=AssetScreeningUnsupervisedLearning_1()
            ),
        )
        if result is None:
            return

        st.markdown("Resultados do screening:")
        st.dataframe(result["df"])

        st.markdown("Gráfico:")
        render_unsupervised_learning_1_chart(
            data=result["df"],
            X_scaled=result["X_scaled"],
            ativo_destaque="KLBN11",
        )

        st.markdown("Código Python utilizado:")
        st.code(
            """
            from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import AssetScreeningUnsupervisedLearning_1, get_eligible_assets_unsupervised_learning_1
            df: DataFrame = get_eligible_assets_unsupervised_learning_1(service=AssetScreeningUnsupervisedLearning_1())
            """,
            language="python",
            line_numbers=True,
            wrap_lines=True,
        )
        
        st.markdown("Códigos de negociação por cluster:")
        for cluster_id in sorted(result["df"]["cluster"].unique()):
            codes = result["df"].loc[result["df"]["cluster"] == cluster_id, "cod"].tolist()
            with st.expander(f"Cluster {cluster_id} — {len(codes)} ativos"):
                st.code(", ".join(codes), language=None)



st.title("Asset Screening")
st.write("Explore os diferentes screenings de ativos abaixo:")

tab_10y, tab_unsupervised = styled_tabs_widget(
    ["Screening 10y Price 10y ITR", "Screening Unsupervised Learning 1"]
)

render_screening_10y_price_10y_itr(tab_10y)
render_screening_unsupervised_learning_1(tab_unsupervised)