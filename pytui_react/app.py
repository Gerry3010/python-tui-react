from __future__ import annotations
from textual import events
from textual.app import App as TextualApp, ComposeResult
from .base import Component

class App(TextualApp):
    """Main application class for pytui-react."""

    CSS = """
    Screen {
        layers: base dialog;
    }
    """

    def __init__(self, root: Component, **kwargs):
        super().__init__(**kwargs)
        self.root = root

    def compose(self) -> ComposeResult:
        yield self.root

    def on_key(self, event: events.Key) -> None:
        # Mirrors Component.on_key: handles useKey(..., global_key=True) bindings
        # registered without a description (those skip Textual's Binding system).
        if hasattr(self, "_key_handlers") and event.key in self._key_handlers:
            self._key_handlers[event.key]()
            event.stop()

    def action_hook_dispatch(self, action_id: str) -> None:
        # Mirrors Component.action_hook_dispatch: dispatches useKey(..., global_key=True,
        # description=...) bindings, which are registered on the App (not a Component).
        if hasattr(self, "_binding_handlers") and action_id in self._binding_handlers:
            self._binding_handlers[action_id]()

def run(root: Component) -> None:
    """Helper function to run the application."""
    app = App(root)
    app.run()
