from pytui_react import Component, Label, Button, Vertical, useState, run

class Counter(Component):
    def build(self):
        # State hook for the counter
        count, set_count = useState(0)
        
        with Vertical(styles={"align": ("center", "middle"), "border": ("heavy", "blue")}):
            Label(f"Counter Value: [bold cyan]{count}[/]", styles={"margin": (1, 0)})
            
            with Vertical(styles={"width": "auto"}):
                Button("Increment", on_click=lambda: set_count(count + 1), variant="success")
                Button("Decrement", on_click=lambda: set_count(count - 1), variant="error")
                Button("Reset", on_click=lambda: set_count(0), variant="primary")

if __name__ == "__main__":
    run(Counter())
