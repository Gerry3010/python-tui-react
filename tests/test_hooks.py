import pytest
from pytui_react import App, Component, useState, useEffect
from pytui_react.widgets import Label, Button, Vertical
from textual.widgets import Label as TextualLabel

class Counter(Component):
    def build(self):
        count, set_count = useState(0)
        with Vertical():
            Label(f"Count: {count}", id="count-label")
            Button("Increment", on_click=lambda: set_count(count + 1), id="inc-btn")

@pytest.mark.asyncio
async def test_use_state():
    app = App(Counter())
    async with app.run_test() as pilot:
        # Check initial state
        label = app.screen.query_one("#count-label", TextualLabel)
        assert str(label.content) == "Count: 0"
        
        # Click button
        await pilot.click("#inc-btn")
        # Wait for re-render
        await pilot.pause()
        
        # Check updated state
        label = app.screen.query_one("#count-label", TextualLabel)
        assert str(label.content) == "Count: 1"

        # Click again
        await pilot.click("#inc-btn")
        await pilot.pause()
        label = app.screen.query_one("#count-label", TextualLabel)
        assert str(label.content) == "Count: 2"

class EffectComp(Component):
    def __init__(self, log_func, **kwargs):
        super().__init__(**kwargs)
        self.log_func = log_func

    def build(self):
        count, set_count = useState(0)
        
        def effect():
            self.log_func("mount")
            return lambda: self.log_func("cleanup")
        
        useEffect(effect, [count])
        
        with Vertical():
            Label(f"Count: {count}")
            Button("Inc", on_click=lambda: set_count(count + 1), id="inc")

@pytest.mark.asyncio
async def test_use_effect():
    logs = []
    def log(msg):
        logs.append(msg)
        
    app = App(EffectComp(log))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert "mount" in logs
        logs.clear()
        
        # Trigger update
        await pilot.click("#inc")
        await pilot.pause()
        
        assert "cleanup" in logs
        assert "mount" in logs
        logs.clear()
        
    # Unmount should trigger cleanup
    # In Textual tests, closing the app or pilot finishing should unmount
    assert "cleanup" in logs

from pytui_react import createContext, useContext, ContextProvider

MyContext = createContext("default")

class Consumer(Component):
    def build(self):
        val = useContext(MyContext)
        Label(f"Value: {val}", id="context-val")

class ProviderWrapper(Component):
    def build(self):
        with ContextProvider(MyContext, "provided"):
            Consumer()

@pytest.mark.asyncio
async def test_use_context():
    # Test default value
    app_default = App(Consumer())
    async with app_default.run_test():
        label = app_default.screen.query_one("#context-val", TextualLabel)
        assert str(label.content) == "Value: default"
        
    # Test provided value
    app_provided = App(ProviderWrapper())
    async with app_provided.run_test():
        label = app_provided.screen.query_one("#context-val", TextualLabel)
        assert str(label.content) == "Value: provided"
