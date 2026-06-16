from __future__ import annotations
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

def run(root: Component) -> None:
    """Helper function to run the application."""
    app = App(root)
    app.run()
