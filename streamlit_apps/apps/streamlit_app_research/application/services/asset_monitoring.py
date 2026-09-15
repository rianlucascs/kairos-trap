

from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import AssetPriceService
from streamlit_apps.apps.streamlit_app_research.application.analytics import (
    MovingAverageDistanceAnalysis,
    PriceRegressionAnalysis,
    DrawdownAnalysis
)

class AssetMonitoring:
    
    
    def __init__(
        self, 
        result: dict, # get_eligible_assets_unsupervised_learning_1(service=AssetScreeningUnsupervisedLearning_1()
        cluster: int = 3
    ) -> None:
        
        self.result = result
        self.cluster = cluster
        
        self.asset_price_service = AssetPriceService()


    def get_assets_by_cluster(self):
        return self.result["df"].loc[self.result["df"]["cluster"] == self.cluster]["cod"].apply(lambda x: x+".SA").to_list()
    
    
    def get_stats_by_ticker(self):
        
        stats = {}
        
        for ticker in self.get_assets_by_cluster():
            
            price = self.asset_price_service.get_asset_price(tickers=ticker, period="10y", interval="1d")
            
            stats[ticker] = {
                "date_last_price": price["Date"].iloc[-1].strftime("%Y-%m-%d"),
                "last_price": price["Adj Close"].iloc[-1],
                "current_distance_media20%": MovingAverageDistanceAnalysis(price, 20).current,
                "current_distance_regression%": PriceRegressionAnalysis(price).current,
                "current_drawdown%": DrawdownAnalysis(price).current,
            }

        return stats