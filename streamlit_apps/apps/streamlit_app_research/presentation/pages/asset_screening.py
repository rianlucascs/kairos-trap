

from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import (
    AssetScreening10yPrice10yITRService,
    get_eligible_assets,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components import styled_tabs_widget

from dataclasses import dataclass
from typing import Optional
import streamlit as st
from pandas import DataFrame


@dataclass
class ScreeningDTO:
    name: Optional[str]
    description: Optional[str]
    data: Optional[DataFrame]
    python: Optional[str]


screenings: list[ScreeningDTO] = [
    ScreeningDTO(
        name="Screening 10y Price 10y ITR",
        description=AssetScreening10yPrice10yITRService.__doc__,
        data=get_eligible_assets(service=AssetScreening10yPrice10yITRService()),
        python="""
        from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening import AssetScreening10yPrice10yITRService, get_eligible_assets
        df: DataFrame = get_eligible_assets(service=AssetScreening10yPrice10yITRService())
        """,
    ),
    ScreeningDTO(
        name=None,
        description=None,
        data=None,
        python=None,
    ),
]

st.title("Asset Screening")
st.write("Explore os diferentes screenigs de ativos abaixo:")

for screening_dto in screenings:
    st.markdown(
        f"- **{screening_dto.name}** — {screening_dto.description}",
        unsafe_allow_html=True,
    )

tab_labels = [screening_dto.name or "Em breve" for screening_dto in screenings]
tabs = styled_tabs_widget(tab_labels)

for tab, screening_dto in zip(tabs, screenings):
    
    with tab:
        
        if screening_dto.data is not None:
            
            st.markdown("Resultados do screening:")
            st.dataframe(screening_dto.data)
            
            st.markdown("Código Python utilizado:")
            st.code(screening_dto.python, language="python", line_numbers=True, wrap_lines=True)
            
        else:
            
            st.info("Screening ainda não disponível.")
            