from pytui_react import App, Component, useState
from pytui_react.widgets import Vertical, Label, Button

class ScrollingList(Component):
    def build(self):
        items, set_items = useState(list(range(50)))
        
        with Vertical(styles={"height": "100%", "border": "solid green", "overflow_y": "scroll"}):
            Label("Scrollable List of Items:")
            for i in items:
                Label(f"Item {i}")
            Button("Add Item", on_click=lambda: set_items(items + [len(items)]))

if __name__ == "__main__":
    App(ScrollingList()).run()
