from pytui_react import App, Component, useState
from pytui_react.widgets import ListView, ListItem, Label, Vertical

class ListViewExample(Component):
    def build(self):
        selected, set_selected = useState("None")
        
        def handle_select(event):
            # Textual's event has the item. We can access the first child's renderable if it's a Label
            try:
                # This is a bit internal to Textual, but for demonstration:
                label_text = event.item.query_one(Label).renderable
                set_selected(str(label_text))
            except Exception:
                set_selected("Unknown")

        with Vertical():
            Label(f"Selected: [bold magenta]{selected}[/bold magenta]")
            with ListView(on_selected=handle_select, styles={"border": "sunken blue", "margin": 1}):
                for i in range(1, 11):
                    with ListItem():
                        Label(f"List Item {i}")

if __name__ == "__main__":
    App(ListViewExample()).run()
