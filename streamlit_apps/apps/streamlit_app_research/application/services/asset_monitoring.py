

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
    ) -> None:
        
        self.result = result

        self.asset_price_service = AssetPriceService()


    def get_assets_by_cluster(self, cluster: int) -> list[str]:
        df = self.result["df"]
        return (df.loc[df["cluster"] == cluster, "cod"] + ".SA").tolist()

    
    def get_clusters(self) -> list:
        return sorted(self.result["df"]["cluster"].unique().tolist())
    

    def get_assets_by_all_clusters(self) -> dict[int, list[str]]:
        return {c: self.get_assets_by_cluster(c) for c in self.get_clusters()}


    def get_stats_by_ticker(self, cluster):
        
        stats = {}
        
        for ticker in self.get_assets_by_cluster(cluster    ):
            
            price = self.asset_price_service.get_asset_price(tickers=ticker, period="10y", interval="1d")
            
            stats[ticker] = {
                "date_last_price": price["Date"].iloc[-1].strftime("%Y-%m-%d"),
                "last_price": price["Adj Close"].iloc[-1],
                "current_distance_media20%": MovingAverageDistanceAnalysis(price, 20).current,
                "current_distance_regression%": PriceRegressionAnalysis(price).current,
                "current_drawdown%": DrawdownAnalysis(price).current,
            }

        return stats