from __future__ import annotations
from typing import Any, Callable, Optional
from textual.widget import Widget
from textual.widgets import (
    Label as TextualLabel,
    Button as TextualButton,
    Input as TextualInput,
    ListView as TextualListView,
    ListItem as TextualListItem
)
from textual.containers import Container as TextualContainer, Vertical as TextualVertical, Horizontal as TextualHorizontal
from .base import register_widget, UIBuilder

def _apply_styles(widget: Widget, styles: Optional[dict] = None) -> None:
    if styles:
        for key, value in styles.items():
            try:
                setattr(widget.styles, key, value)
            except Exception:
                pass # TODO: Log warning for invalid style property

class Container(TextualContainer):
    def __init__(self, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets

class Vertical(TextualVertical):
    def __init__(self, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets

class Horizontal(TextualHorizontal):
    def __init__(self, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets

class Button(TextualButton):
    def __init__(self, label: str, on_click: Optional[Callable] = None, styles: Optional[dict] = None, **kwargs):
        super().__init__(label, **kwargs)
        _apply_styles(self, styles)
        self.on_click_handler = on_click
        register_widget(self)

    def on_button_pressed(self) -> None:
        if self.on_click_handler:
            self.on_click_handler()

class ContextProvider(Container):
    def __init__(self, context: Any, value: Any, **kwargs):
        super().__init__(**kwargs)
        self.context = context
        self.value = value

    def __enter__(self):
        UIBuilder.push_context(self.context, self.value)
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        UIBuilder.pop_context()
        return super().__exit__(exc_type, exc_val, exc_tb)

def Label(text: str, styles: Optional[dict] = None, **kwargs) -> TextualLabel:
    widget = TextualLabel(text, **kwargs)
    _apply_styles(widget, styles)
    return register_widget(widget)

def Input(value: str = "", placeholder: str = "", styles: Optional[dict] = None, **kwargs) -> TextualInput:
    widget = TextualInput(value=value, placeholder=placeholder, **kwargs)
    _apply_styles(widget, styles)
    return register_widget(widget)

class ListView(TextualListView):
    def __init__(self, on_selected: Optional[Callable] = None, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        self.on_selected_handler = on_selected
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets

    def on_list_view_selected(self, event: TextualListView.Selected) -> None:
        if self.on_selected_handler:
            self.on_selected_handler(event)

class ListItem(TextualListItem):
    def __init__(self, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets
