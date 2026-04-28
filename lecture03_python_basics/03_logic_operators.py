"""
03 — Logical Operators
======================
Combine conditions into trading signals.
Run this file:  python 03_logic_operators.py
"""

price = 195.00
moving_average = 200.00
rsi = 28
volume = 60_000_000
avg_volume = 45_000_000

# and — all conditions must be True
buy_signal = rsi < 30 and price < moving_average
print(f"RSI={rsi}, Price<MA={price < moving_average}")
print(f"Buy signal (RSI<30 AND below MA): {buy_signal}")

# or — at least one condition must be True
high_activity = volume > avg_volume * 1.5 or price < moving_average * 0.95
print(f"\nHigh activity (volume spike OR price crash): {high_activity}")

# not — flip a boolean
market_open = False
waiting = not market_open
print(f"\nMarket open: {market_open}")
print(f"Waiting for market: {waiting}")

# Combining all three
panic_sell = not market_open and (rsi > 80 or price < 100)
print(f"\nPanic sell? {panic_sell}")

# Practical pattern: checking if a value is in a safe range
in_neutral_zone = 30 <= rsi <= 70  # Python allows chained comparison!
print(f"\nRSI {rsi} in neutral zone (30-70): {in_neutral_zone}")
