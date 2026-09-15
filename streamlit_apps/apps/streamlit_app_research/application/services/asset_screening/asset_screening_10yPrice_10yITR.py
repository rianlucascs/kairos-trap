

from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.cvm_formulario_informacoes_trimestrais_repository import CVMFormularioInformacoesTrimestraisRepository as itr
from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.yfinance_price_provider_repository import YFinancePriceProviderRepository as YFProvider
from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.b3_indices_segmentos_setoriais_repository import B3IndicesSegmentosSetoriaisRepository as b3_indices
from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.b3_enriquecimento_cadastral_ativos_repository import B3EnriquecimentoCadastralAtivosRepository as b3_enriquecimento

from pandas import DataFrame, to_datetime
from datetime import timedelta


class AssetScreening10yPrice10yITRService:
    """
    Filtra os ativos elegíveis com base no histórico de 10 anos de preço e ITR,
    e ordena os resultados pelo volume financeiro médio em ordem decrescente (ascending=False).
    """
    

    MIN_YEARS = 10


    def _get_ibov_composition(self) -> DataFrame:
        
        b3_index_df = b3_indices(file_identifiers="composicao.parquet").read().copy()
        
        return b3_index_df[b3_index_df["index"] == "IBOV"].reset_index(drop=True)


    def _get_price_stats(self, ibov_df: DataFrame) -> DataFrame:
        
        price_stats = {}

        for row in ibov_df.itertuples():
            price_df = YFProvider().get_asset_price(
                tickers=row.cod + ".SA", period="max", interval="1d"
            ).copy()

            price_stats[row.cod] = {
                "date_start_price": price_df.index.min(),
                "date_end_price": price_df.index.max(),
                "ma_volume_financeiro": price_df["Volume"].mean(),
            }

        return (
            DataFrame.from_dict(price_stats, orient="index")
            .rename_axis("cod")
            .reset_index()
        )


    def _get_cvm_codes(self) -> DataFrame:
        
        cvm_codes_df = b3_enriquecimento(file_identifiers="codigos.parquet").read()
        cvm_codes_df.rename(columns={"code": "cod"}, inplace=True)
        
        return cvm_codes_df


    def _get_itr_stats(self, assets_df: DataFrame) -> DataFrame:
        
        itr_stats = {}

        for row in assets_df.itertuples():
            itr_df = itr("BPP_con").query_parquet(
                filters={"CD_CVM": str(row.codeCVM).zfill(6)}
            )

            itr_stats[row.codeCVM] = {
                "date_start_itr": itr_df["DT_REFER"].min(),
                "date_end_itr": itr_df["DT_REFER"].max(),
            }

        return (
            DataFrame.from_dict(itr_stats, orient="index")
            .rename_axis("codeCVM")
            .reset_index()
        )


    def _add_years_diff_columns(self, df: DataFrame) -> DataFrame:
        
        diff_dias_preco = (
            to_datetime(df["date_end_price"], format="%Y-%m-%d") - df["date_start_price"]
        )
        
        df["anos_diferenca_preco"] = (diff_dias_preco.dt.days / 365.25).astype(int)

        diff_dias_itr = (
            to_datetime(df["date_end_itr"], format="%Y-%m-%d") - df["date_start_itr"]
        )
        
        df["anos_diferenca_itr"] = (diff_dias_itr.dt.days / 365.25).astype(int)

        return df


    def _filter_and_sort_eligible_assets(self, df: DataFrame) -> DataFrame:
        
        columns = [
            "cod",
            "asset",
            "codeCVM",
            "anos_diferenca_preco",
            "anos_diferenca_itr",
            "ma_volume_financeiro",
        ]

        return (
            df[
                (df["anos_diferenca_itr"] >= self.MIN_YEARS)
                & (df["anos_diferenca_preco"] >= self.MIN_YEARS)
            ]
            .sort_values(by="ma_volume_financeiro", ascending=False)[columns]
            .reset_index(drop=True)
        )


    def _process(self) -> DataFrame:
        
        ibov_df = self._get_ibov_composition()

        price_stats_df = self._get_price_stats(ibov_df)
        assets_with_price_stats_df = ibov_df.merge(price_stats_df, on="cod", how="left")

        cvm_codes_df = self._get_cvm_codes()
        assets_with_cvm_codes_df = assets_with_price_stats_df.merge(
            cvm_codes_df, on="cod", how="left"
        )

        itr_stats_df = self._get_itr_stats(assets_with_cvm_codes_df)
        assets_with_itr_stats_df = assets_with_cvm_codes_df.merge(
            itr_stats_df, on="codeCVM", how="left"
        )

        eligible_assets_df = self._add_years_diff_columns(assets_with_itr_stats_df)

        return self._filter_and_sort_eligible_assets(eligible_assets_df)


from streamlit_apps.apps.streamlit_app_research.application.ttl_disk_cache import TTLDiskCache


_eligible_assets_cache = TTLDiskCache(
    name="asset_screening_10yPrice_10yITR",
    ttl=timedelta(days=1),
    show_spinner="Filtrando ativos elegíveis...",
)


@_eligible_assets_cache.wrap
def _get_eligible_assets_cached(_service: "AssetScreening10yPrice10yITRService") -> DataFrame:
    return _service._process()


def get_eligible_assets_10yPrice10yITR(service: "AssetScreening10yPrice10yITRService") -> DataFrame:
    return _eligible_assets_cache.get(_service=service)
