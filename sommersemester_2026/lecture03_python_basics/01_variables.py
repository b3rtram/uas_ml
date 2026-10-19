"""
01 — Variables & Types
======================
Every piece of stock data has a type.
Run this file:  python 01_variables.py
"""

# str — the ticker symbol
ticker = "AAPL"

# float — prices always have decimals
price = 215.49
previous_close = 211.30

# int — volume is a whole number (shares traded today)
volume = 48_350_000  # underscores are allowed for readability

# bool — is the stock going up?
is_rising = price > previous_close

# printing
print(f"Ticker:   {ticker}")
print(f"Price:    ${price}")
print(f"Volume:   {volume:,}")
print(f"Rising?   {is_rising}")

# check types with type()
print()
print(f"type(ticker)  = {type(ticker)}")   # <class 'str'>
print(f"type(price)   = {type(price)}")    # <class 'float'>
print(f"type(volume)  = {type(volume)}")   # <class 'int'>
print(f"type(is_rising) = {type(is_rising)}")  # <class 'bool'>
