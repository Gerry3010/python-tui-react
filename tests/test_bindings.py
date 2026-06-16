import pytest
from pytui_react import App, Component, useKey, useState
from pytui_react.widgets import Footer, Vertical, Label

class BindingComp(Component):
    def build(self):
        count, set_count = useState(0)
        useKey("f1", lambda: set_count(count + 1), description="Help")
        with Vertical():
            Label(f"Count: {count}", id="label")
            Footer()

@pytest.mark.asyncio
async def test_footer_bindings_functional():
    app = App(BindingComp())
    async with app.run_test() as pilot:
        app.root.can_focus = True
        app.root.focus()
        await pilot.pause()
        label = app.screen.query_one("#label")
        assert label.content == "Count: 0"
        
        # Trigger the binding action
        # In Textual, we can use app.run_action or pilot.press
        await pilot.press("f1")
        await pilot.pause()
        
        label = app.screen.query_one("#label")
        assert label.content == "Count: 1"
