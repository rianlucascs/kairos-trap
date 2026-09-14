

from pandas import DataFrame
import numpy as np


class ReturnVolatilityAnalysis:


    def __init__(
        self,
        price: DataFrame,
        window: int = 21,
    ) -> None:
        
        returns = (
            price["Adj Close"]
            .pct_change(fill_method=None)
            .dropna()
        )
        
        volatility = returns.rolling(window).std()
        mean_return = returns.rolling(window).mean()

        data = DataFrame(
            {
                "volatility": volatility,
                "mean_return": mean_return,
            }
        ).dropna()

        self.data = data

        self.mean_volatility = data["volatility"].mean()
        self.mean_return = data["mean_return"].mean()
        
        self.current_volatility = lambda lookback=1: data["volatility"].iloc[-lookback]
        self.current_return = lambda lookback=1: data["mean_return"].iloc[-lookback]

        self.r2 = self._calculate_r2()

        self.ellipse_x, self.ellipse_y = self._calculate_ellipse()


    def _calculate_r2(self) -> float:
        
        x = self.data["volatility"]
        y = self.data["mean_return"]

        coef = np.polyfit(x, y, 1)
        y_pred = np.polyval(coef, x)

        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)

        return 1 - ss_res / ss_tot


    def _calculate_ellipse(self):
        
        x = self.data["volatility"]
        y = self.data["mean_return"]

        covariance = np.cov(x, y)

        values, vectors = np.linalg.eigh(covariance)

        order = values.argsort()[::-1]

        values = values[order]
        vectors = vectors[:, order]

        angle = np.linspace(0, 2 * np.pi, 200)

        ellipse = (
            2
            * np.sqrt(values[:, None])
            * np.array([
                np.cos(angle),
                np.sin(angle),
            ])
        )

        rotated = vectors @ ellipse

        ellipse_x = self.mean_volatility + rotated[0]
        ellipse_y = self.mean_return + rotated[1]

        return ellipse_x, ellipse_y