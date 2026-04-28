"""
10 — Dictionaries
==================
Manage a stock portfolio with key-value pairs.
Run this file:  python 10_dictionaries.py
"""

# A portfolio: ticker → number of shares
portfolio = {
    "AAPL": 50,
    "MSFT": 30,
    "GOOGL": 20,
}

# Current prices
prices = {
    "AAPL": 215.50,
    "MSFT": 420.10,
    "GOOGL": 175.30,
}

# Access by key
print(f"AAPL shares: {portfolio['AAPL']}")
print(f"AAPL price:  ${prices['AAPL']}")

# Add a new position
portfolio["SAP.DE"] = 100
prices["SAP.DE"] = 195.80
print(f"\nAdded SAP.DE: {portfolio['SAP.DE']} shares @ ${prices['SAP.DE']}")

# Calculate portfolio value
print("\n--- Portfolio value ---")
total_value = 0

for ticker, shares in portfolio.items():
    value = shares * prices[ticker]
    total_value += value
    print(f"  {ticker:8s}: {shares:3d} shares × ${prices[ticker]:8.2f} = ${value:10,.2f}")

print(f"  {'':8s}  {'':34s} ──────────")
print(f"  {'Total':8s}  {'':34s} ${total_value:10,.2f}")

# Safe access with .get() — no crash if key is missing
tesla_shares = portfolio.get("TSLA", 0)
print(f"\nTSLA shares: {tesla_shares} (not in portfolio)")

# All tickers
print(f"\nHoldings: {list(portfolio.keys())}")
