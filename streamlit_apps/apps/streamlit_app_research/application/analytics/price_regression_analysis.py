

from pandas import DataFrame
import numpy as np
from scipy.stats import linregress


class PriceRegressionAnalysis:


    def __init__(
        self,
        price: DataFrame,
        moving_average: int | None = None,
    ) -> None:
        
        data = price[["Date", "Adj Close"]].dropna().copy()

        if moving_average:
            data["Adj Close"] = (
                data["Adj Close"]
                .rolling(moving_average)
                .mean()
            )
            data = data.dropna()

        x = np.arange(len(data))
        y = data["Adj Close"].to_numpy()

        regression = linregress(x, y)

        trend = regression.intercept + regression.slope * x

        distance_pct = ((y - trend) / trend) * 100

        self.data = data
        self.distance_pct = distance_pct
        self.mean = distance_pct.mean()
        self.std = distance_pct.std()
        self.current = distance_pct[-1]