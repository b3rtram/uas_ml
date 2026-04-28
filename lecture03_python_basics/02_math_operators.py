"""
02 — Math Operators
===================
Calculate stock returns and positions.
Run this file:  python 02_math_operators.py
"""

buy_price = 150.00
sell_price = 185.50
shares = 10

# Basic arithmetic
profit_per_share = sell_price - buy_price
total_profit = profit_per_share * shares

# Percentage return
return_pct = (sell_price - buy_price) / buy_price * 100

# Integer division & remainder
trading_days = 252
weeks = trading_days // 5       # 50 full weeks
remaining_days = trading_days % 5  # 2 days left over

# Power — compound growth
annual_return = 0.08  # 8% per year
years = 10
growth_factor = (1 + annual_return) ** years  # 2.159...

print(f"Buy:           ${buy_price}")
print(f"Sell:          ${sell_price}")
print(f"Shares:        {shares}")
print(f"Profit/share:  ${profit_per_share:.2f}")
print(f"Total profit:  ${total_profit:.2f}")
print(f"Return:        {return_pct:.1f}%")
print()
print(f"{trading_days} trading days = {weeks} weeks + {remaining_days} days")
print(f"$1000 at {annual_return:.0%}/yr for {years} yrs = ${1000 * growth_factor:.2f}")
