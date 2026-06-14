"""
11 — Classes
============
Model a stock with its own data and methods.
Run this file:  python 11_classes.py
"""


class Stock:
    """Represents a stock with price history."""

    def __init__(self, ticker, prices):
        self.ticker = ticker
        self.prices = prices   # list of closing prices

    def latest(self):
        """Return the most recent price."""
        return self.prices[-1]

    def average(self):
        """Simple average of all prices."""
        return sum(self.prices) / len(self.prices)

    def highest(self):
        return max(self.prices)

    def lowest(self):
        return min(self.prices)

    def daily_returns(self):
        """Percentage change from day to day."""
        returns = []
        for i in range(1, len(self.prices)):
            r = (self.prices[i] - self.prices[i - 1]) / self.prices[i - 1] * 100
            returns.append(r)
        return returns

    def summary(self):
        """Print a quick overview."""
        print(f"--- {self.ticker} ---")
        print(f"  Latest:  ${self.latest():.2f}")
        print(f"  Average: ${self.average():.2f}")
        print(f"  High:    ${self.highest():.2f}")
        print(f"  Low:     ${self.lowest():.2f}")
        rets = self.daily_returns()
        if rets:
            print(f"  Best day:  {max(rets):+.2f}%")
            print(f"  Worst day: {min(rets):+.2f}%")


# --- Using the class ---

aapl = Stock("AAPL", [214.29, 216.75, 213.49, 219.86, 220.27])
msft = Stock("MSFT", [415.20, 418.50, 420.10, 417.85, 422.30])

aapl.summary()
print()
msft.summary()

# Each instance has its own data
print(f"\nAAPL average: ${aapl.average():.2f}")
print(f"MSFT average: ${msft.average():.2f}")
