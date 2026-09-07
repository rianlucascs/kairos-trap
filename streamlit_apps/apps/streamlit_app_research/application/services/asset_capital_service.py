
from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_capital_repository import AssetCapitalRepository

from pandas import DataFrame
import streamlit as st


class AssetCapitalService:


    def __init__(self) -> None:

        self.asset_capital_repository = AssetCapitalRepository()


    @st.cache_data(ttl=60*5, show_spinner="Loading capital data...")
    def get_quantidade_total_acoes(_self, cd_cvm: str) -> DataFrame:
        return _self.asset_capital_repository.get_quantidade_total_acoes(cd_cvm=cd_cvm)


    @st.cache_data(ttl=60*5, show_spinner="Loading dividend data...")
    def get_dividendos_pagos(_self, cd_cvm: str) -> DataFrame:
        return _self.asset_capital_repository.get_dividendos_pagos(cd_cvm=cd_cvm)
