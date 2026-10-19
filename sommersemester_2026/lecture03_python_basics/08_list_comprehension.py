"""
08 — List Comprehensions
========================
Filter and transform stock data in one line.
Run this file:  python 08_list_comprehension.py
"""

prices = [214.29, 216.75, 213.49, 219.86, 220.27,
          218.50, 222.14, 225.00, 221.33, 223.85]

# --- Transform: daily returns as percentages ---
# Long way:
returns = []
for i in range(1, len(prices)):
    r = (prices[i] - prices[i - 1]) / prices[i - 1] * 100
    returns.append(r)

# Comprehension:
returns = [(prices[i] - prices[i - 1]) / prices[i - 1] * 100
           for i in range(1, len(prices))]

print("Daily returns:")
for i, r in enumerate(returns):
    print(f"  Day {i + 2}: {r:+.2f}%")

# --- Filter: only the positive days ---
up_days = [r for r in returns if r > 0]
print(f"\nUp days:   {len(up_days)} of {len(returns)}")
print(f"Down days: {len(returns) - len(up_days)}")

# --- Transform + Filter: prices above 220 as strings ---
high_prices = [f"${p:.2f}" for p in prices if p > 220]
print(f"\nPrices above $220: {high_prices}")

# --- Bonus: dict comprehension ---
tickers = ["AAPL", "MSFT", "GOOGL"]
current_prices = [215.50, 420.10, 175.30]

portfolio = {t: p for t, p in zip(tickers, current_prices)}
print(f"\nPortfolio dict: {portfolio}")
