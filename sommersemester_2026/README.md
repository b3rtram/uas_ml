# Python Basics — Stock Examples 📈

One Python file per concept from Session 4, all using stock market examples.

## How to run

```bash
cd examples
python 01_variables.py
python 02_math_operators.py
# ... etc.
```

No external libraries needed — everything runs with plain Python 3.11+.

## The examples

| # | File | Concept | Stock Example |
|---|------|---------|---------------|
| 01 | `01_variables.py` | Variables & Types | Ticker, price, volume, is_rising |
| 02 | `02_math_operators.py` | Math Operators | Return calculation, compound growth |
| 03 | `03_logic_operators.py` | Logical Operators | Buy signal (RSI + MA conditions) |
| 04 | `04_if_else.py` | if / elif / else | RSI zone classification |
| 05 | `05_while_loop.py` | while Loop | Wait for price to hit target |
| 06 | `06_for_loop.py` | for Loop | Average closing price over a week |
| 07 | `07_lists.py` | Lists | Portfolio of prices, min/max/sort |
| 08 | `08_list_comprehension.py` | List Comprehension | Filter up-days, transform prices |
| 09 | `09_functions.py` | Functions | calculate_return(), moving_average() |
| 10 | `10_dictionaries.py` | Dictionaries | Portfolio as {ticker: shares} |
| 11 | `11_classes.py` | Classes | Stock class with methods |
| 12 | `12_decorators.py` | Decorators | @dataclass Stock, @property value |
| 13 | `13_modules.py` | Modules & Imports | Simulated indicators.py import |
| 14 | `14_exceptions.py` | Exceptions | Safe user input, missing ticker |

## Tip

Read each file top to bottom — the comments explain what's happening.
Then try modifying the numbers and rerunning. Break things on purpose.
That's how you learn.
