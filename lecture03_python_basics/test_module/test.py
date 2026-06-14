class Stock:
    """Represents a stock with price history."""
    
    def __init__(self, ticker, prices):
        self.ticker = ticker
        self.prices = prices   # list of closing prices

    def moving_average(self, prices, window=5):
        """Simple moving average."""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window


    def daily_returns(self, prices):
        """Percentage returns."""
        return [(prices[i] - prices[i - 1]) / prices[i - 1] * 100
                for i in range(1, len(prices))]
