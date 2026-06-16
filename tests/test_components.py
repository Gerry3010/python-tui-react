import pytest
from pytui_react import App, Component
from pytui_react.widgets import Label, Vertical, Horizontal, Container
from textual.widgets import Label as TextualLabel

class NestedComp(Component):
    def build(self):
        with Vertical(id="outer"):
            Label("Outer")
            with Horizontal(id="inner"):
                Label("Inner 1")
                Label("Inner 2")
            with Container(id="box"):
                Label("Boxed")

@pytest.mark.asyncio
async def test_nesting():
    app = App(NestedComp())
    async with app.run_test():
        # Check structure
        outer = app.screen.query_one("#outer", Vertical)
        inner = app.screen.query_one("#inner", Horizontal)
        box = app.screen.query_one("#box", Container)
        
        # Verify children
        # outer has Label, Horizontal, Container
        assert len(outer.children) == 3
        
        # inner has 2 Labels
        assert len(inner.children) == 2
        assert str(inner.query(TextualLabel)[0].content) == "Inner 1"
        assert str(inner.query(TextualLabel)[1].content) == "Inner 2"
        
        # box has 1 Label
        assert len(box.children) == 1
        assert str(box.query_one(TextualLabel).content) == "Boxed"
