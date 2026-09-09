
from streamlit_apps.apps.streamlit_app_research.presentation.components.styled_tabs_widget import styled_tabs

from streamlit_apps.apps.streamlit_app_research.application.services.asset_eligibility_A_service import AssetEligibilityAService


import streamlit as st
from typing import Callable, Optional
from dataclasses import dataclass


asset_eligibility_A_service = AssetEligibilityAService()


@dataclass
class FilterTab:
    
    description: str
    widget: Optional[Callable[[], None]] = None

    
FILTERS = {
    "A": FilterTab(
        description="Ativos com pelo menos 10 anos de dados de preços e ITR, ordenados pelo volume financeiro médio.",
        widget= lambda : st.dataframe(asset_eligibility_A_service.get("IBOV"))
    ),
    "B": FilterTab(
        description="...", 
        widget=None
    ),
}

for key, value in FILTERS.items():
    st.markdown(f"**Filter {key.upper()}:** {value.description}")

tabs = styled_tabs(list(FILTERS.keys()))

for tab_key, tab in zip(FILTERS, tabs):
    
    with tab:
        
        if FILTERS[tab_key].widget is not None:
            FILTERS[tab_key].widget()