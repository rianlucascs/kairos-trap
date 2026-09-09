
from streamlit_apps.apps.streamlit_app_research.application.services.asset_b3_sector_indices_services import AssetB3SectorIndicesService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_demonstration_service import AssetDemonstrationService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import AssetPriceService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_service import AssetService


from pandas import DataFrame, to_datetime


class AssetEligibilityAService:
    
    
    def __init__(
        self,
    ) -> None:
        
        self._b3_sector_indices_service = AssetB3SectorIndicesService()
        self._asset_price_service = AssetPriceService()
        self._asset_service = AssetService()
        self._demonstration_service = AssetDemonstrationService()
        
    
    def _get_stats_price(self, asset):
        return self._asset_price_service.get_asset_price(tickers=asset, period="max", interval="1d").copy()
    
    
    def _build_price_stats(self, b3_index_select):
        
        price_stats = {}

        for row in b3_index_select.itertuples():
            
            price_df = self._get_stats_price(asset=row.cod+".SA").reset_index()
            
            price_stats[row.cod] = {
                "date_start_price": price_df.index.min(),
                "date_end_price": price_df.index.max(),
                "ma_volume_financeiro": price_df["Volume"].mean(),
                "anos_diferenca_preco": int((price_df["Date"].max() - price_df["Date"].min()).days / 365.25)
                }
         
        price_stats_df = (
            DataFrame.from_dict(price_stats, orient="index")
            .rename_axis("cod")
            .reset_index()
        )

        return price_stats_df
    
    
    def build_stats_demonstration(self, assets_with_cvm_codes_df):
        
        demonstration_stats = {}
        
        for row in assets_with_cvm_codes_df.itertuples():
            
            if type(row.codeCVM) is not str:
                continue
            
            demonstration_df = self._demonstration_service.get_demonstration(cd_cvm=row.codeCVM, demonstration_code="BPA_con", prefix="itr+dfp", cd_conta="1")
            
            diff_dias_demonstration = int((demonstration_df["DT_REFER"].max() - demonstration_df["DT_REFER"].min()).days / 365.25)
            
            demonstration_stats[row.codeCVM] = {"anos_diferenca_demonstracao": diff_dias_demonstration}
            
        demonstration_stats_df = (
            DataFrame.from_dict(demonstration_stats, orient="index")
            .rename_axis("codeCVM")
            .reset_index()
        )
        
        return demonstration_stats_df
        
        
    def get(self, index):
        
        b3_index_select = self._b3_sector_indices_service.get_composition_by_index(index)
        
        # Filtro preço
        price_stats_df = self._build_price_stats(b3_index_select)
        filter_stats_price_df = price_stats_df[price_stats_df["anos_diferenca_preco"] >= 10].reset_index(drop=True)
        assets_with_price_stats_df = b3_index_select.merge(filter_stats_price_df, on="cod", how="left")
                
        # Adicionar dados complementares
        cvm_codes_df = self._asset_service.get_companies()
        cvm_codes_df.rename(columns={"code": "cod"}, inplace=True)
        assets_with_cvm_codes_df = assets_with_price_stats_df.merge(cvm_codes_df, on="cod", how="left")
    
            
        demonstration_stats_df = self.build_stats_demonstration(assets_with_cvm_codes_df)
        filter_stats_demonstration_df = demonstration_stats_df[demonstration_stats_df["anos_diferenca_demonstracao"] >= 10].reset_index(drop=True)
        eligible_assets_df = assets_with_cvm_codes_df.merge(filter_stats_demonstration_df, on="codeCVM", how="left")
        
        return eligible_assets_df
    