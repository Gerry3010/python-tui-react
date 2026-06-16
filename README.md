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

### Routing

#### `Router` / `Routes` / `Route` / `Link`
`Router` holds the current location and provides it to descendants. `Routes` renders the first child `Route` whose `path` matches. `Link` navigates without replacing the whole app.
```python
with Router():
    Navbar()
    with Routes():
        with Route("/"):
            Home()
        with Route("/about"):
            About()
```

Use `:name` segments for dynamic params, read them with `useParams()`:
```python
with Route("/user/:id"):
    UserProfile()

class UserProfile(Component):
    def build(self):
        params = useParams()
        Label(f"User: {params['id']}")
```

`useLocation()` returns the current path, e.g. to highlight the active nav link.

#### `DialogRoute` / `DialogOutlet`
For detail views that should overlay the current page instead of replacing it, use `DialogRoute` together with a `DialogOutlet`. The outlet must be placed explicitly in the tree (it is not mounted automatically by `Router`/`App`):
```python
with Routes():
    with Route("/"):
        UserList()
with DialogOutlet():
    with DialogRoute("/user/:id"):
        UserDetailDialog()
```
Navigate into the dialog with `Link(to, label, dialog=True)`, or `navigate(path, dialog=True)` from `useNavigate()`. Close it with `useCloseDialog()`, by navigating to a non-dialog path, or by pressing Escape (handled by the `Dialog` widget).

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
- `04_scrolling.py`: Scrollable containers.
- `05_list_view.py`: `ListView`/`ListItem` and selection handling.
- `06_framework_extensions.py`: Custom hooks and widgets.
- `07_routing.py`: `Router`/`Routes`/`Route`/`Link` navigation.
- `08_dynamic_routing.py`: Dynamic path params with `useParams()`.
- `09_dialog_routes.py`: Modal detail views with `DialogRoute`/`DialogOutlet`.
