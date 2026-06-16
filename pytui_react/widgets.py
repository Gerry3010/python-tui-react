from __future__ import annotations
from typing import Any, Callable, Optional
from textual.widget import Widget
from textual.widgets import (
    Label as TextualLabel,
    Button as TextualButton,
    Input as TextualInput,
    ListView as TextualListView,
    ListItem as TextualListItem,
    Header as TextualHeader,
    Footer as TextualFooter
)
from textual.widgets._header import HeaderTitle
from textual.containers import Container as TextualContainer, Vertical as TextualVertical, Horizontal as TextualHorizontal
from textual.css.query import NoMatches
from textual.dom import NoScreen
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

class Dialog(TextualContainer):
    """A full-screen overlay that centers its content, used for modal/detail routes."""

    DEFAULT_CSS = """
    Dialog {
        layer: dialog;
        dock: top;
        width: 100%;
        height: 100%;
        align: center middle;
        background: $background 60%;
    }
    Dialog > Container {
        width: auto;
        height: auto;
        min-width: 30;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    """
    can_focus = True

    def __init__(self, on_close: Optional[Callable] = None, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        self.on_close = on_close
        register_widget(self)
        self._builder = UIBuilder()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield TextualContainer(*self._builder.widgets)

    def on_mount(self) -> None:
        self.focus()

    def on_key(self, event) -> None:
        if event.key == "escape" and self.on_close is not None:
            self.on_close()
            event.stop()

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

def _safe_header_on_mount(self, _) -> None:
    """Replacement for Header._on_mount that tolerates being stale after unmount.

    pytui_react re-renders by recreating widgets like Header on every build(),
    but Header._on_mount() subscribes its set_title callback to the
    app/screen "title"/"sub_title" reactives via self.watch(...). That
    subscription is never cleaned up on unmount (textual.reactive._watch
    appends permanently to obj.__watchers), so every previously-unmounted
    Header still fires set_title() on the next title change. Upstream only
    guards against NoScreen; once this Header's own HeaderTitle child is gone
    too it raises NoMatches instead, which Textual treats as fatal and exits
    the whole app. This patches Header._on_mount itself (rather than
    subclassing) because Textual dispatches lifecycle handlers like
    `_on_mount` once per class in the MRO, so a subclass override would run
    *alongside*, not instead of, the original unsafe handler.
    """
    async def set_title() -> None:
        try:
            self.query_one(HeaderTitle).update(self.format_title())
        except (NoScreen, NoMatches):
            pass

    self.watch(self.app, "title", set_title)
    self.watch(self.app, "sub_title", set_title)
    self.watch(self.screen, "title", set_title)
    self.watch(self.screen, "sub_title", set_title)

TextualHeader._on_mount = _safe_header_on_mount

def Header(*args, **kwargs) -> TextualHeader:
    return register_widget(TextualHeader(*args, **kwargs))

def Footer(*args, **kwargs) -> TextualFooter:
    return register_widget(TextualFooter(*args, **kwargs))

class ListView(TextualListView):
    def __init__(self, on_selected: Optional[Callable] = None, styles: Optional[dict] = None, auto_focus: bool = False, **kwargs):
        super().__init__(**kwargs)
        _apply_styles(self, styles)
        self.on_selected_handler = on_selected
        self.auto_focus = auto_focus
        register_widget(self)
        self._builder = UIBuilder()

    def on_mount(self) -> None:
        if self.auto_focus:
            self.focus()

    def __enter__(self):
        return self._builder.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._builder.__exit__(exc_type, exc_val, exc_tb)

    def compose(self):
        yield from self._builder.widgets

    def on_list_view_selected(self, event: TextualListView.Selected) -> None:
        self._handle_selection(event)

    def on_list_item_activated(self, event: TextualListItem.Activated) -> None:
        self._handle_selection(event)

    def _handle_selection(self, event: Any) -> None:
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
