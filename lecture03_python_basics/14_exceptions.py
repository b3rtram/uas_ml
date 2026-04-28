"""
14 — Exceptions
===============
Handle errors gracefully when dealing with stock data.
Run this file:  python 14_exceptions.py
"""


def get_price_from_user():
    """Ask the user for a stock price — handle bad input."""
    while True:
        try:
            text = input("Enter stock price: $")
            price = float(text)
            if price <= 0:
                print("Price must be positive. Try again.")
                continue
            return price
        except ValueError:
            print(f"'{text}' is not a valid number. Try again.")


def safe_return(buy_price, sell_price):
    """Calculate return, handling division by zero."""
    try:
        return (sell_price - buy_price) / buy_price * 100
    except ZeroDivisionError:
        print("Error: buy price cannot be zero.")
        return None


def lookup_price(portfolio, ticker):
    """Look up a ticker in the portfolio, handle missing keys."""
    try:
        return portfolio[ticker]
    except KeyError:
        print(f"'{ticker}' not found in portfolio.")
        return None


# --- Demo ---

# 1. Safe dictionary lookup
print("--- Portfolio lookup ---")
portfolio = {"AAPL": 215.50, "MSFT": 420.10}

for ticker in ["AAPL", "TSLA", "MSFT"]:
    price = lookup_price(portfolio, ticker)
    if price is not None:           # note: `is not None`, not `!= None`
        print(f"  {ticker}: ${price:.2f}")

# 2. Safe return calculation
print("\n--- Return calculation ---")
print(f"  Normal:   {safe_return(150, 185):.1f}%")
print(f"  Zero buy: {safe_return(0, 185)}")

# 3. User input (uncomment to try interactively)
# print("\n--- Interactive ---")
# price = get_price_from_user()
# print(f"You entered: ${price:.2f}")

# Common exception types you'll see:
#   ValueError      — wrong value (e.g. float("hello"))
#   KeyError        — missing dict key
#   IndexError      — list index out of range
#   FileNotFoundError — file doesn't exist
#   ZeroDivisionError — dividing by zero
#   TypeError       — wrong type (e.g. "abc" + 5)
