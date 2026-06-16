# Pytui-React

A React-inspired declarative TUI library for Python, built on top of [Textual](https://textual.textualize.io/).

## Features

- **Component-based**: Build UI using reusable components.
- **Context Manager Syntax**: Define UI hierarchy using Python's `with` blocks.
- **Hooks**: Manage state and side effects with `useState`, `useEffect`, and `useContext`.
- **Easy Styling**: Inline styles support for common CSS properties.

## Installation

```bash
# Assuming you have the library files in your project
pip install textual
```

## Quick Start

```python
from pytui_react import Component, Label, Button, Vertical, useState, run

class Counter(Component):
    def build(self):
        count, set_count = useState(0)
        
        with Vertical():
            Label(f"Counter: {count}")
            Button("Increment", on_click=lambda: set_count(count + 1))

if __name__ == "__main__":
    run(Counter())
```

## Documentation

### Hooks

#### `useState(initial_value)`
Returns a tuple containing the current state and a setter function.
```python
count, set_count = useState(0)
```

#### `useEffect(callback, dependencies)`
Runs a side effect after the component is rendered.
Returns a cleanup function (optional).
```python
def effect():
    print("Mounted")
    return lambda: print("Unmounted")
useEffect(effect, [])
```

#### `useContext(context)`
Consumes a value from a `ContextProvider`.
```python
theme = useContext(ThemeContext)
```

### Components

#### `Component`
The base class for all components. Override the `build` method to define UI.

#### `ContextProvider`
Provides a context value to all nested components.
```python
with ContextProvider(MyContext, "value"):
    MyChild()
```

#### Standard Widgets
- `Label(text, styles=None)`
- `Button(label, on_click=None, styles=None)`
- `Input(value, placeholder, styles=None)`
- `Container(styles=None)`
- `Vertical(styles=None)`
- `Horizontal(styles=None)`

## Examples

Check the `examples/` directory for more comprehensive examples:
- `01_counter.py`: Basic state management.
- `02_effects.py`: Side effects and timers.
- `03_context.py`: Sharing data with Context.
