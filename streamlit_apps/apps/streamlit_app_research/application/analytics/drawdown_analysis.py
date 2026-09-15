

class DrawdownAnalysis:
    
    
    def __init__(
        self, 
        price
    ) -> None:
        
        self.price = price
        self.drawdown = self._calculate_drawdown()
        self.current = self.drawdown.iloc[-1]
    
    
    def _calculate_drawdown(self):
        
        peak = self.price["Adj Close"].expanding(min_periods=1).max()
        drawdown = (self.price["Adj Close"] - peak) / peak * 100
        
        return drawdown