"""
04 — if / elif / else
=====================
Classify RSI into trading zones.
Run this file:  python 04_if_else.py
"""

rsi = 72

# Simple if/else
if rsi > 70:
    signal = "OVERBOUGHT — consider selling"
elif rsi < 30:
    signal = "OVERSOLD — consider buying"
else:
    signal = "NEUTRAL — hold"

print(f"RSI: {rsi}")
print(f"Signal: {signal}")

# More complex: position sizing based on conviction
print("\n--- Position sizing ---")
confidence = 0.85  # how sure are we (0 to 1)
portfolio_value = 100_000

if confidence >= 0.9:
    position_pct = 0.10  # 10% of portfolio
elif confidence >= 0.7:
    position_pct = 0.05  # 5%
elif confidence >= 0.5:
    position_pct = 0.02  # 2%
else:
    position_pct = 0.0   # skip it
    print("Confidence too low — no trade.")

position_value = portfolio_value * position_pct
print(f"Confidence: {confidence:.0%}")
print(f"Position:   {position_pct:.0%} of portfolio = ${position_value:,.0f}")

# --- Combining conditions with and, or, not ---
print("\n--- Trading signals with and / or / not ---")

price = 195.00
moving_average = 200.00
volume = 60_000_000
market_open = True

# and — ALL conditions must be True
buy_signal = rsi < 30 and price < moving_average and market_open
print(f"Buy signal (RSI<30 AND below MA AND market open): {buy_signal}")

# or — at least ONE condition must be True
worth_watching = rsi > 70 or rsi < 30 or volume > 50_000_000
print(f"Worth watching (extreme RSI OR high volume):      {worth_watching}")

# not — flips True to False and vice versa
if not market_open:
    print("Market is closed — no trading today.")
else:
    print("Market is open — let's go.")

# Combining all three in a real scenario
strong_buy = (rsi < 30 and price < moving_average) and not (volume < 10_000_000)
print(f"\nStrong buy (oversold AND below MA, but NOT low volume): {strong_buy}")

# Bonus: Python allows chained comparison — reads like math
in_neutral_zone = 30 <= rsi <= 70
print(f"RSI {rsi} in neutral zone (30-70): {in_neutral_zone}")