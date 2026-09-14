

from streamlit_apps.apps.streamlit_app_research.application.services.asset_demonstration_service import AssetDemonstrationService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_capital_service import AssetCapitalService

from pandas import DataFrame, merge_asof
import streamlit as st


class AssetFundamentalIndicatorService:
    """
    Indicadores fundamentalistas que dependem de dado de mercado (preço e nº de ações), combinando
    demonstrações financeiras da CVM (AssetDemonstrationService) com capital social e dividendos
    do Formulário de Referência (AssetCapitalService). `preco` é o DataFrame retornado por
    AssetPriceService.get_asset_price (colunas "Date", "Close"). Usa "Close" (não "Adj Close") pois
    o ajuste retroativo de dividendos/splits distorce razões preço/fundamento em datas passadas.
    """


    def __init__(self) -> None:

        self.asset_demonstration_service = AssetDemonstrationService()
        self.asset_capital_service = AssetCapitalService()


    def _as_of(self, spine: DataFrame, other: DataFrame, value_column: str) -> DataFrame:
        """Traz `value_column` de `other` (frequência menor: anual/diária) para o grid de `spine`, usando o último valor disponível até a data (sem look-ahead)."""

        spine = spine.sort_values("DT_REFER")
        other = other[["DT_REFER", value_column]].sort_values("DT_REFER")

        return merge_asof(spine, other, on="DT_REFER", direction="backward")


    def _get_valor_de_mercado(self, cd_cvm: str, preco: DataFrame, spine: DataFrame) -> DataFrame:
        """Valor de mercado (preço x nº de ações) no grid de datas de `spine`, em R$ mil (mesma escala das demonstrações da CVM)."""

        acoes = self.asset_capital_service.get_quantidade_total_acoes(cd_cvm=cd_cvm).rename(columns={"VL_CONTA_TRI": "N_ACOES"})
        preco_normalizado = preco[["Date", "Close"]].rename(columns={"Date": "DT_REFER", "Close": "PRECO"})

        grid = spine[["DT_REFER"]].drop_duplicates()
        grid = self._as_of(grid, acoes, "N_ACOES")
        grid = self._as_of(grid, preco_normalizado, "PRECO")

        return grid.assign(VL_CONTA_TRI=lambda df: (df["N_ACOES"] * df["PRECO"]) / 1000)[["DT_REFER", "VL_CONTA_TRI"]]


    @st.cache_data(ttl=60*5, show_spinner="Calculando valor de mercado...")
    def get_valor_de_mercado(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        # Grid diário (datas do próprio preço), para refletir a cotação mais recente disponível.
        spine = preco[["Date"]].rename(columns={"Date": "DT_REFER"})
        return _self._get_valor_de_mercado(cd_cvm=cd_cvm, preco=preco, spine=spine)


    @st.cache_data(ttl=60*5, show_spinner="Calculando P/L...")
    def get_pl(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        lucro_liquido_ltm = _self.asset_demonstration_service.get_lucro_liquido_ltm(cd_cvm=cd_cvm)
        valor_de_mercado = _self._get_valor_de_mercado(cd_cvm=cd_cvm, preco=preco, spine=lucro_liquido_ltm)

        return (
            valor_de_mercado
            .merge(lucro_liquido_ltm, on="DT_REFER", suffixes=("_mercado", "_lucro"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_mercado"] / df["VL_CONTA_TRI_lucro"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Calculando P/VP...")
    def get_pvp(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        patrimonio_liquido = _self.asset_demonstration_service.get_patrimonio_liquido_total(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        valor_de_mercado = _self._get_valor_de_mercado(cd_cvm=cd_cvm, preco=preco, spine=patrimonio_liquido)

        return (
            valor_de_mercado
            .merge(patrimonio_liquido, on="DT_REFER", suffixes=("_mercado", "_pl"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_mercado"] / df["VL_CONTA_TRI_pl"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Calculando PSR...")
    def get_psr(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        receita_liquida_ltm = _self.asset_demonstration_service.get_receita_liquida_ltm(cd_cvm=cd_cvm)
        valor_de_mercado = _self._get_valor_de_mercado(cd_cvm=cd_cvm, preco=preco, spine=receita_liquida_ltm)

        return (
            valor_de_mercado
            .merge(receita_liquida_ltm, on="DT_REFER", suffixes=("_mercado", "_receita"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_mercado"] / df["VL_CONTA_TRI_receita"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Calculando EV/EBIT...")
    def get_ev_ebit(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        ebit_ltm = _self.asset_demonstration_service.get_ebit_ltm(cd_cvm=cd_cvm)
        divida_liquida = _self.asset_demonstration_service.get_divida_liquida(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        valor_de_mercado = _self._get_valor_de_mercado(cd_cvm=cd_cvm, preco=preco, spine=ebit_ltm)

        return (
            valor_de_mercado
            .merge(divida_liquida, on="DT_REFER", how="left", suffixes=("_mercado", "_divida"))
            .merge(ebit_ltm.rename(columns={"VL_CONTA_TRI": "VL_CONTA_TRI_ebit"}), on="DT_REFER")
            .assign(
                VL_CONTA_TRI_divida=lambda df: df["VL_CONTA_TRI_divida"].fillna(0),
                VL_CONTA_TRI=lambda df: (df["VL_CONTA_TRI_mercado"] + df["VL_CONTA_TRI_divida"]) / df["VL_CONTA_TRI_ebit"],
            )
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Calculando Dividend Yield...")
    def get_dividend_yield(_self, cd_cvm: str, preco: DataFrame) -> DataFrame:
        # Granularidade anual (por exercício social), pela própria natureza do dado de dividendos
        # do Formulário de Referência; não há como decompor em trimestres.
        dividendos = _self.asset_capital_service.get_dividendos_pagos(cd_cvm=cd_cvm)
        acoes = _self.asset_capital_service.get_quantidade_total_acoes(cd_cvm=cd_cvm).rename(columns={"VL_CONTA_TRI": "N_ACOES"})
        preco_normalizado = preco[["Date", "Close"]].rename(columns={"Date": "DT_REFER", "Close": "PRECO"})

        grid = _self._as_of(dividendos, acoes, "N_ACOES")
        grid = _self._as_of(grid, preco_normalizado, "PRECO")

        return (
            grid
            .assign(VL_CONTA_TRI=lambda df: (df["VL_CONTA_TRI"] / df["N_ACOES"]) / df["PRECO"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )
