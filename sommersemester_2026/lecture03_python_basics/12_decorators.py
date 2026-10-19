"""
12 — Decorators
===============
Use @dataclass and @property to write cleaner stock classes.
Run this file:  python 12_decorators.py
"""

from dataclasses import dataclass


@dataclass
class Stock:
    """A stock — Python writes __init__, __repr__, __eq__ for us."""
    ticker: str
    price: float
    shares: int = 0

    @property
    def value(self):
        """Calculated field — call it like an attribute, not a method."""
        return self.price * self.shares

    @property
    def label(self):
        return f"{self.ticker} @ ${self.price:.2f}"
    
    @staticmethod
    def market_status():
        return "Open"  # In a real app, this would check


# @dataclass auto-generates __init__:
aapl = Stock(ticker="AAPL", price=215.50, shares=50)
msft = Stock(ticker="MSFT", price=420.10, shares=30)

# @dataclass auto-generates __repr__:
print(aapl)
# Output: Stock(ticker='AAPL', price=215.5, shares=50)

# @property lets you access .value like a variable (no parentheses):
print(f"\n{aapl.label}")
print(f"  Position value: ${aapl.value:,.2f}")

print(f"\n{msft.label}")
print(f"  Position value: ${msft.value:,.2f}")

total = aapl.value + msft.value
print(f"\nPortfolio total: ${total:,.2f}")

# @dataclass auto-generates __eq__:
same = Stock("AAPL", 215.50, 50)
print(f"\naapl == same? {aapl == same}")   # True — compares field values

# without @dataclass
class Stock:
    def __init__(self, ticker: str, price: float, shares: int = 0):
        self.ticker = ticker
        self.price = price
        self.shares = shares

    def __repr__(self):
        return f"Stock(ticker={self.ticker!r}, price={self.price!r}, shares={self.shares!r})"

    def __eq__(self, other):
        if not isinstance(other, Stock):
            return NotImplemented
        return (self.ticker, self.price, self.shares) == (other.ticker, other.price, other.shares)
