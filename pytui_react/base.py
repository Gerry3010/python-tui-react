from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Any, Generator, TypeVar, Generic

if TYPE_CHECKING:
    from textual.app import ComposeResult

from textual.widget import Widget

class UIBuilder:
    """A context manager to collect widgets defined in a 'with' block."""
    _stack: List[UIBuilder] = []
    _current_component: Optional[Component] = None
    _context_stack: List[dict] = []

    def __init__(self):
        self.widgets: List[Widget] = []

    def __enter__(self) -> UIBuilder:
        UIBuilder._stack.append(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        UIBuilder._stack.pop()

    @classmethod
    def get_current(cls) -> Optional[UIBuilder]:
        return cls._stack[-1] if cls._stack else None

    @classmethod
    def get_current_component(cls) -> Optional[Component]:
        return cls._current_component

    @classmethod
    def push_context(cls, context: Any, value: Any) -> None:
        cls._context_stack.append({context: value})

    @classmethod
    def pop_context(cls) -> None:
        cls._context_stack.pop()

    @classmethod
    def get_context_value(cls, context: Any) -> Any:
        for frame in reversed(cls._context_stack):
            if context in frame:
                return frame[context]
        return getattr(context, "default_value", None)

    def add(self, widget: Widget) -> None:
        self.widgets.append(widget)

def register_widget(widget: Widget) -> Widget:
    """Registers a widget with the current UIBuilder if one exists."""
    builder = UIBuilder.get_current()
    if builder:
        builder.add(widget)
    return widget

class Component(Widget):
    """Base class for React-like components."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._hooks: List[Any] = []
        self._hook_index: int = 0
        self._context_snapshot: List[dict] = list(UIBuilder._context_stack)
        register_widget(self)
    
    def compose(self) -> ComposeResult:
        old_comp = UIBuilder._current_component
        UIBuilder._current_component = self
        self._hook_index = 0
        try:
            with UIBuilder() as builder:
                self.build()
                yield from builder.widgets
        finally:
            UIBuilder._current_component = old_comp

    def on_unmount(self) -> None:
        from .hooks import EffectState
        for state in self._hooks:
            if isinstance(state, EffectState) and state.cleanup:
                try:
                    state.cleanup()
                except Exception:
                    pass

    def build(self) -> None:
        """Override this method to define the UI structure."""
        pass

    def re_render(self) -> None:
        """Triggers a re-render of the component."""
        coro = self.recompose()
        try:
            self.run_worker(coro)
        except Exception:
            # Fallback if run_worker is not available or fails
            pass
