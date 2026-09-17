

import pandas as pd


class MonthlyCumulativeReturnAnalysis:
    """
    Gera uma tabela única de retornos mensais: linhas = ano, colunas = mês
    (formato clássico de tabela de retorno mensal).

    `price` já deve vir mensalizado (ex: via to_monthly()), com o último
    preço disponível de cada mês, incluindo o mês corrente em andamento.
    `window` define quantos dos meses mais recentes considerar.
    """


    def __init__(self, adj_close: pd.Series, window: int):
        self.adj_close = adj_close
        self.window = window
        self.result = self.calculate_monthly_cumulative_return()


    def calculate_monthly_cumulative_return(self) -> pd.DataFrame:
        if not isinstance(self.adj_close.index, pd.DatetimeIndex):
            raise TypeError("price precisa ter um DatetimeIndex")

        monthly_return = self.adj_close.pct_change().dropna()
        monthly_return = monthly_return.tail(self.window)

        table = monthly_return.to_frame(name="return")
        table["year"] = table.index.year
        table["month"] = table.index.month

        pivot = table.pivot(index="year", columns="month", values="return")
        pivot = pivot.rename(
            columns={m: pd.Timestamp(2000, m, 1).strftime("%b") for m in pivot.columns}
        )

        pivot["Anual"] = pivot.apply(
            lambda row: (1 + row.dropna()).prod() - 1, axis=1
        )

        return pivot.reset_index().rename(columns={"year": "Ano"})