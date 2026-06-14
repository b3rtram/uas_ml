"""
06 — for Loop
=============
Calculate the average closing price over a week.
Run this file:  python 06_for_loop.py
"""

# A week of AAPL closing prices
closing_prices = [214.29, 216.75, 213.49, 219.86, 220.27]

# Calculate the average — step by step
total = 0
for price in closing_prices:
    total = total + price

average = total / len(closing_prices)
print(f"Prices: {closing_prices}")
print(f"Average: ${average:.2f}")

# Find the highest and lowest day
print("\n--- Daily report ---")
for i in range(len(closing_prices)):
    day_name = ["Mon", "Tue", "Wed", "Thu", "Fri"][i]
    price = closing_prices[i]

    if price == max(closing_prices):
        label = "  ← highest"
    elif price == min(closing_prices):
        label = "  ← lowest"
    else:
        label = ""

    print(f"  {day_name}: ${price:.2f}{label}")

# Using enumerate (cleaner way to get index + value)
print("\n--- With enumerate ---")
for i, price in enumerate(closing_prices):
    daily_return = 0 if i == 0 else (price - closing_prices[i - 1]) / closing_prices[i - 1] * 100
    print(f"  Day {i + 1}: ${price:.2f}  ({daily_return:+.2f}%)")
