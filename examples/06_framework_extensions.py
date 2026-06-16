from pytui_react import App, Component, useState, useInterval, useKey, useApp, useFocus
from pytui_react.widgets import Vertical, Label, Button, Header, Footer, Container

class ExtensionExample(Component):
    def build(self):
        app = useApp()
        time_count, set_time_count = useState(0)
        key_pressed, set_key_pressed = useState("None")
        
        # Clock effect
        useInterval(lambda: set_time_count(lambda c: c + 1), 1.0)
        
        # Global key handlers with footer descriptions
        useKey("escape", lambda: app.exit(), description="Exit")
        useKey("backspace", lambda: set_key_pressed("Backspace"), description="Clear Key")
        useKey("q", lambda: app.exit(), show=False) # Hidden binding

        with Vertical():
            Header()
            with Container(styles={"height": "1fr", "align": "center middle"}):
                Label(f"Time running: [bold green]{time_count}s[/bold green]")
                Label(f"Last special key: [bold magenta]{key_pressed}[/bold magenta]")
                Label("Press 'Esc' or 'q' to exit.")
                
                with FocusableButton("I grab focus initially", auto_focus=True):
                    pass
                
                with FocusableButton("I also react to focus"):
                    pass
            Footer()

class FocusableButton(Component):
    def build(self):
        focused, grab_focus = useFocus()
        
        styles = {
            "border": "solid white",
            "padding": 1,
            "margin": 1,
            "background": "blue" if focused else "black"
        }
        
        with Container(styles=styles):
            Label(f"{self.renderable_name} - {'[B]FOCUSED[/]' if focused else 'Unfocused'}")
            if not focused:
                Button("Click to Focus", on_click=grab_focus)

if __name__ == "__main__":
    App(ExtensionExample()).run()
