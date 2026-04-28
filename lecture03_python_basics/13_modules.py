"""
13 — Modules & Imports
======================
Split stock analysis code into reusable files.
Run this file:  python 13_modules.py

This example is self-contained: we define a helper module inline and
import from it. In a real project, indicators.py would be a separate file.
"""

# In a real project you'd have this in indicators.py:
# --------------------------------------------------
# def moving_average(prices, window=5):
#     if len(prices) < window:
#         return None
#     return sum(prices[-window:]) / window
#
# def rsi(prices, window=14):
#     ...
# --------------------------------------------------
# And in main.py:
#     from indicators import moving_average, rsi

# Since this is a single-file example, we simulate the import
# by defining the functions here (imagine them in indicators.py):

from lecture03_python_basics.test_module.test import moving_average, daily_returns   # ← this is the "import" statement

# --- Main script (imagine: from indicators import moving_average, daily_returns) ---

prices = [214.29, 216.75, 213.49, 219.86, 220.27,
          218.50, 222.14, 225.00, 221.33, 223.85]

print("--- Stock Analysis ---")
print(f"Latest price: ${prices[-1]:.2f}")
print(f"5-day MA:     ${moving_average(prices, 5):.2f}")
print(f"10-day MA:    ${moving_average(prices, 10):.2f}")

rets = daily_returns(prices)
print(f"\nDaily returns:")
for i, r in enumerate(rets):
    arrow = "↑" if r > 0 else "↓"
    print(f"  Day {i + 2}: {r:+.2f}% {arrow}")

print(f"\nAvg return: {sum(rets) / len(rets):+.2f}%")

