

from yfinance import download
from pandas import DataFrame, MultiIndex
from pandas import DataFrame, concat, offsets


class YFinancePriceProviderError(Exception):
    pass


class YFinancePriceProvider:
    """
    Provedor de preços de ativos utilizando o Yahoo Finance.
    """


    def _normalize(self, df: DataFrame) -> DataFrame:
        
        if isinstance(df.columns, MultiIndex):
            df = df.droplevel(1, axis=1)

        return df.sort_index()


    def _validate(self, df: DataFrame) -> None:
        
        if df.empty:
            
            raise YFinancePriceProviderError(
                "DataFrame baixado está vazio."
            )

        if df.iloc[-1].isna().any():
            
            print("DataFrame contém valores NaN na última linha.")
            
        return df
            


    def get_asset_price(self, **kwargs) -> DataFrame:
        """
        Obtém os preços históricos de um ativo usando o Yahoo Finance.

        Args:
            **kwargs: Argumentos que serão passados para a função `yfinance.download`.

        Returns:
            DataFrame: DataFrame contendo os preços históricos do ativo.
        """
        
        df = download(**kwargs, progress=False, auto_adjust=False)

        self._validate(df)

        return self._normalize(df)
    

    def get_assets_prices(
        self,
        assets: list[str],
        period: str = "10y",
        interval: str = "1d",
    ) -> dict[str, DataFrame]:
        """
        Obtém os preços históricos de múltiplos ativos usando o Yahoo Finance.

        Args:
            assets (list[str]): Lista de códigos dos ativos.
            period (str): Período de tempo para os dados históricos (padrão: "10y").
            interval (str): Intervalo de tempo dos dados (padrão: "1d").

        Returns:
            dict[str, DataFrame]: Dicionário onde as chaves são os códigos dos ativos e os valores são os DataFrames com os preços históricos.
        """
        
        prices_by_code = {}

        for asset in assets:
            df = self.get_asset_price(
                tickers=asset,
                period=period,
                interval=interval,
            )

            if not df.empty:
                prices_by_code[asset] = df

        
        if not prices_by_code:
            
            raise YFinancePriceProviderError(
                "Nenhum dado de preço foi baixado para os ativos fornecidos."
            )
        
        return prices_by_code


    def to_monthly(df: DataFrame) -> DataFrame:
        """
        Transforma uma série temporal diária em uma série mensal, usando o último registro disponível de cada mês.
        
        Garantindo que o último mês seja incluído mesmo que ainda não tenha terminado.
        """

        df_month = df.resample("ME").last()

        last = df.iloc[[-1]]

        if last.index[0] != last.index[0] + offsets.MonthEnd(0):
            last.index = [last.index[0] + offsets.MonthEnd(0)]
            df_month = concat([df_month, last])

        return df_month[~df_month.index.duplicated(keep="last")]