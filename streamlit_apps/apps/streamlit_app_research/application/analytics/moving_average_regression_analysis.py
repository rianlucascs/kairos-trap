

from pandas import DataFrame


class MovingAverageDistanceAnalysis:
    
    
    def __init__(
        self,
        price: DataFrame,
        moving_average: int = 20,
    ) -> None:
        
        data = price[["Date", "Adj Close"]].dropna().copy()
        
        ma = data["Adj Close"].rolling(window=moving_average).mean()

        distance_pct = ((data["Adj Close"] - ma) / ma) * 100

        self.data = data
        self.moving_average = ma
        self.distance_pct = distance_pct
        self.mean = distance_pct.mean()
        self.std = distance_pct.std()
        self.current = distance_pct.iloc[-1]