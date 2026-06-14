"""
09 — Functions
==============
Reusable calculations for stock analysis.
Run this file:  python 09_functions.py
"""


# def calculate_return(buy_price, sell_price):
#     """Calculate the percentage return of a trade."""
#     return (sell_price - buy_price) / buy_price * 100


# def moving_average(prices, window=5):
#     """Simple moving average over the last `window` prices.

#     Returns None if not enough data.
#     """
#     if len(prices) < window:
#         return None
#     return sum(prices[-window:]) / window


# def is_buy_signal(price, ma, rsi, rsi_threshold=30):
#     """Simple buy signal: price below MA and RSI oversold."""
#     return price < ma and rsi < rsi_threshold


# # --- Using the functions ---

# # Trade return
# buy = 150.00
# sell = 185.50
# print(f"Buy ${buy:.2f} → Sell ${sell:.2f}")
# print(f"Return: {calculate_return(buy, sell):.1f}%")

# # Moving average
# prices = [214.29, 216.75, 213.49, 219.86, 220.27,
#           218.50, 222.14, 225.00, 221.33, 223.85]

# ma5 = moving_average(prices, window=5)
# ma10 = moving_average(prices, window=10)
# print(f"\n5-day MA:  ${ma5:.2f}")
# print(f"10-day MA: ${ma10:.2f}")

# # Buy signal
# current_price = 195.00
# current_rsi = 25
# signal = is_buy_signal(current_price, ma5, current_rsi)
# print(f"\nPrice=${current_price}, MA=${ma5:.2f}, RSI={current_rsi}")
# print(f"Buy signal? {signal}")

# # You can call functions with different parameters:
# print(f"\nWith RSI threshold 40: {is_buy_signal(current_price, ma5, current_rsi, rsi_threshold=40)}")


def average(numbers, ignore_non_numbers=False):
    if ignore_non_numbers:
        numbers = [n for n in numbers if isinstance(n, (int, float))]
    total = sum(numbers)
    count = len(numbers)
    return total / count

grades = [85, 72, 91, 68, 77]
grades = ["A", "B", "C"]  # This will cause an error when we try to average
try:
    print(average(grades))
except TypeError as e:
    print(f"Error unkown")

print ("I dont care about the error, I just want to print this")