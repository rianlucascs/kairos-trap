
from datetime import timedelta

import numpy as np
from pandas import DataFrame
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from data_providers.providers.yfinance_price_provider import YFinancePriceProvider
from streamlit_apps.apps.streamlit_app_research.application.ttl_disk_cache import TTLDiskCache
from streamlit_apps.apps.streamlit_app_research.application.services.asset_demonstration_service import AssetDemonstrationService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_screening.asset_screening_10yPrice_10yITR import get_eligible_assets_10yPrice10yITR, AssetScreening10yPrice10yITRService


class AssetScreeningUnsupervisedLearning_1:
    """
    Agrupa ativos elegíveis (10y Price/10y ITR) em clusters via K-Means,
    a partir de volatilidade de retorno, liquidez (desvio-padrão do volume
    financeiro) e dívida líquida mediana. Considera apenas ativos com
    lucro líquido médio positivo e preço acima de R$ 9.
    """


    def __init__(self):
        self.df = get_eligible_assets_10yPrice10yITR(service=AssetScreening10yPrice10yITRService())
        self.asset_demonstration_service = AssetDemonstrationService()


    def _get_ret_stats(self, df: DataFrame) -> DataFrame:
        ret_stats = {}

        for row in df.itertuples():
            
            price_df = YFinancePriceProvider().get_asset_price(
                tickers=row.cod + ".SA", period="10y"
            )

            ret = price_df["Adj Close"].pct_change(1)

            try:
                divida_liquida = self.asset_demonstration_service.get_divida_liquida(row.codeCVM)["VL_CONTA_TRI"]
                mediana_divida_liquida = divida_liquida.median()
            except:
                mediana_divida_liquida = None

            try:
                lucro_liquido = self.asset_demonstration_service.get_lucro_liquido(row.codeCVM)["VL_CONTA_TRI"]
                media_lucro_liquido = lucro_liquido.mean()
            except:
                media_lucro_liquido = None

            ret_stats[row.cod] = {
                "last_price": price_df["Close"].iloc[-1],
                "std_volume_financeiro": price_df["Volume"].std(),
                "std_ret": ret.std(),
                "mediana_divida_liquida": mediana_divida_liquida,
                "media_lucro_liquido": media_lucro_liquido,
            }

        return (
            DataFrame.from_dict(ret_stats, orient="index")
            .rename_axis("cod")
            .reset_index()
        )


    def _filter_assets(self, df: DataFrame) -> DataFrame:
        df = df.dropna()
        df = df[df["media_lucro_liquido"] > 0].copy()
        return df[df["last_price"] > 9].copy()
    

    def _cluster_assets(self, df: DataFrame) -> dict:
        features = [
            "std_volume_financeiro",
            "std_ret",
            "mediana_divida_liquida",
        ]

        X = df[features].copy()

        for col in [
            "std_volume_financeiro",
            "mediana_divida_liquida",
        ]:
            X[col] = np.sign(X[col]) * np.log1p(np.abs(X[col]))


        X_scaled = StandardScaler().fit_transform(X)

        labels = KMeans(
            n_clusters=4,
            random_state=42,
            n_init=10,
        ).fit_predict(X_scaled)

        silhouette = silhouette_score(X_scaled, labels)
        
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(X_scaled)

        return {"df": df, "X_scaled": X_scaled, "silhouette": silhouette}


    def _process(self) -> dict:
        stats_df = self._get_ret_stats(self.df)
        assets_with_stats_df = self.df.merge(stats_df, on="cod", how="left")
        filtered_assets_df = self._filter_assets(assets_with_stats_df)
        return self._cluster_assets(filtered_assets_df)


_eligible_assets_cache = TTLDiskCache(
    name="asset_screening_unsupervised_learning_1",
    ttl=timedelta(days=1),
    show_spinner="Agrupando ativos...",
)


@_eligible_assets_cache.wrap
def _get_eligible_assets_cached(
    _service: "AssetScreeningUnsupervisedLearning_1",
):
    return _service._process()


def get_eligible_assets_unsupervised_learning_1(
    service: "AssetScreeningUnsupervisedLearning_1",
):
    return _eligible_assets_cache.get(_service=service)


