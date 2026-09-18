

from pandas import DataFrame
import numpy as np
from scipy.stats import linregress
from itertools import groupby


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

        above_avg_days, below_avg_days = self._compute_streaks()
        self.avg_days_above = above_avg_days
        self.avg_days_below = below_avg_days

        current_days, current_direction = self._compute_current_streak()
        self.current_streak_days = current_days
        self.current_streak_direction = current_direction


    def _compute_streaks(self) -> tuple[float, float]:
        """Return (mean streak length above trend, mean streak length below trend)."""
        signs = np.sign(self.distance_pct)

        above_lengths = []
        below_lengths = []

        for sign, group in groupby(signs):
            length = len(list(group))
            if sign > 0:
                above_lengths.append(length)
            elif sign < 0:
                below_lengths.append(length)
            # sign == 0 (exatamente na tendência) é ignorado

        avg_above = float(np.mean(above_lengths)) if above_lengths else 0.0
        avg_below = float(np.mean(below_lengths)) if below_lengths else 0.0

        return avg_above, avg_below


    def _compute_current_streak(self) -> tuple[int, str]:
        """Return (days in the current streak, 'above' or 'below')."""
        signs = np.sign(self.distance_pct)

        last_sign = signs[-1]
        direction = "above" if last_sign > 0 else "below"

        streak_length = 0
        for sign in reversed(signs):
            if sign == last_sign:
                streak_length += 1
            else:
                break

        return streak_length, direction