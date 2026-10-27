# LynnLibPy

A small Python utility library for console applications.

## Features

- **Styled output:** ANSI colors (named and RGB), bold, italic, underline and more. `styled()` validates every style it receives, `unstyled()` strips all styles from a string again.
- **Cursor control:** move the cursor, hide or show it, and write a character at a given position.
- **Typed input:** `typed_input()` asks the user for a value and returns it as the requested type, or `None` if the input does not fit. Booleans accept `yes`, `y`, `true` and any non-zero number.
- **Time limits:** `run_with_limited_time()` runs a function in a separate process and stops it after a given number of seconds.

## Example

```python
from lynn_lib import COLORS, styled, typed_input, run_with_limited_time

print(styled("Warning", COLORS.Foreground.YELLOW, COLORS.BOLD))

# Ask until the user enters a valid integer
while (age := typed_input("Your age: ", int)) is None:
    pass

# Returns None if the function takes longer than 2 seconds
result = run_with_limited_time(sum, ([1, 2, 3],), {}, 2)
```

## Requirements

Python 3.8 or newer and `typing_extensions`:

```
pip install typing_extensions
```

## Tests

The tests use pytest. They mock user input and capture console output, so they run without a terminal.

```
pip install pytest
pytest
```

GitHub Actions runs pytest on every push and pull request, and pylint on every push.
