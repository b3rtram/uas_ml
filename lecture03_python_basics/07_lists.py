"""
07 — Lists
==========
Build and manipulate a portfolio of stock prices.
Run this file:  python 07_lists.py
"""

# A list of closing prices (last 10 days)
prices = [214.29, 216.75, 213.49, 219.86, 220.27,
          218.50, 222.14, 225.00, 221.33, 223.85]

print(f"All prices:   {prices}")
print(f"First price:  ${prices[0]}")       # index 0
print(f"Last price:   ${prices[-1]}")      # negative index = from the end
print(f"Total days:   {len(prices)}")

# --- Slicing: [start:stop:step] ---
print("\n--- Slicing ---")

# [start:stop] — from start up to (but NOT including) stop
print(f"prices[0:3]   = {prices[0:3]}")     # first 3 days
print(f"prices[2:5]   = {prices[2:5]}")     # days 3, 4, 5

# shortcuts: omit start or stop
print(f"prices[:4]    = {prices[:4]}")      # first 4 (same as [0:4])
print(f"prices[7:]    = {prices[7:]}")      # from day 8 to the end
print(f"prices[-3:]   = {prices[-3:]}")     # last 3 days

# [start:stop:step] — take every nth element
print(f"prices[::2]   = {prices[::2]}")     # every other day
print(f"prices[1::2]  = {prices[1::2]}")    # every other day, starting from day 2

# reverse the list
print(f"prices[::-1]  = {prices[::-1]}")    # all prices, reversed

# practical: first week vs second week
week1 = prices[:5]
week2 = prices[5:]
print(f"\nWeek 1: {week1}  avg = ${sum(week1)/len(week1):.2f}")
print(f"Week 2: {week2}  avg = ${sum(week2)/len(week2):.2f}")

# --- Other list operations ---
print("\n--- Other operations ---")

# Add a new day
prices.append(226.10)
print(f"After append: {len(prices)} days, newest = ${prices[-1]}")

# Find min, max, sum
print(f"Highest: ${max(prices):.2f}")
print(f"Lowest:  ${min(prices):.2f}")
print(f"Average: ${sum(prices) / len(prices):.2f}")

# Sorting (creates a new list, original unchanged)
sorted_prices = sorted(prices)
print(f"\nSorted (asc):  {sorted_prices[:3]} ... {sorted_prices[-3:]}")

# Check membership
target = 220.27
print(f"\n${target} in our data? {target in prices}")

# Build a portfolio — list of ticker strings
portfolio = ["AAPL", "MSFT", "SAP.DE"]
portfolio.append("GOOGL")
portfolio.remove("SAP.DE")
print(f"\nPortfolio: {portfolio}")
