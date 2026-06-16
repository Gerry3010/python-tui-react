from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Any, Generator, TypeVar, Generic

if TYPE_CHECKING:
    from textual.app import ComposeResult

from textual.widget import Widget
from textual import events

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

    def __init__(self, *args: Any, auto_focus: bool = False, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._hooks: List[Any] = []
        self._hook_index: int = 0
        self._context_snapshot: List[dict] = list(UIBuilder._context_stack)
        self.auto_focus = auto_focus
        self._binding_handlers: dict[str, Callable] = {}
        self._children_builder = UIBuilder()
        register_widget(self)

    def __enter__(self) -> UIBuilder:
        return self._children_builder.__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return self._children_builder.__exit__(exc_type, exc_val, exc_tb)

    def render_children(self) -> None:
        """Registers all children captured via 'with' blocks with the current UIBuilder."""
        for widget in self._children_builder.widgets:
            register_widget(widget)
    
    def on_mount(self) -> None:
        if self.auto_focus:
            self.focus()

    def on_key(self, event: events.Key) -> None:
        if hasattr(self, "_key_handlers") and event.key in self._key_handlers:
            self._key_handlers[event.key]()
            event.stop()

    def action_hook_dispatch(self, action_id: str) -> None:
        """Dispatches a binding action to the corresponding hook handler."""
        if action_id in self._binding_handlers:
            self._binding_handlers[action_id]()

    def on_focus(self) -> None:
        if hasattr(self, "_focus_handlers"):
            for handler in self._focus_handlers:
                handler(True)

    def on_blur(self) -> None:
        if hasattr(self, "_focus_handlers"):
            for handler in self._focus_handlers:
                handler(False)

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
