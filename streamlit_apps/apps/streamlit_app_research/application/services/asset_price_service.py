

from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories import YFinancePriceProviderRepository

from pandas import DataFrame
import streamlit as st


class AssetPriceService:
    
    
    def __init__(
        self
    ) -> None:
        
        self.asset_price_repository = YFinancePriceProviderRepository()


    @st.cache_data(ttl=60*5, show_spinner="Loading price data...")
    def get_asset_price(_self, **kwargs) -> DataFrame:
        
        return (
            _self.asset_price_repository.get_asset_price(**kwargs)
            .reset_index()
            )
        
        
    @st.cache_data(ttl=60*5, show_spinner="Loading returns data...")
    def get_asset_returns(_self, **kwargs) -> DataFrame:    
        
        return (
            _self.asset_price_repository
            .get_asset_price(**kwargs)
            .reset_index()
            .assign(
                daily_returns=lambda df: df["Adj Close"].pct_change()
            )
        )