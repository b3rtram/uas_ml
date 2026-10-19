"""
05 — while Loop
===============
Simulate waiting for a stock to hit a target price.
Run this file:  python 05_while_loop.py
"""

import random

# Simulate daily price changes
price = 220.00
target = 200.00
day = 0

print(f"Starting price: ${price:.2f}")
print(f"Target (buy):   ${target:.2f}")
print(f"Waiting...\n")

random.seed(42)  # reproducible results

while price > target:
    # Random daily change between -5% and +3%
    change_pct = random.uniform(-0.05, 0.03)
    price = price * (1 + change_pct)
    day += 1
    print(f"  Day {day:3d}: ${price:.2f}  ({change_pct:+.1%})")

print(f"\nPrice hit ${price:.2f} on day {day} — time to buy!")

# Safety note: always have a maximum wait
# (in real code, use `while price > target and day < 365:`)
