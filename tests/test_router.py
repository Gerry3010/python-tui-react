import pytest
from pytui_react import (
    App, Component, Router, Routes, Route, DialogRoute, DialogOutlet,
    Link, Label, useNavigate, useParams, useCloseDialog, Vertical,
)
from textual.widgets import Label as TextualLabel

class SimpleRouterApp(Component):
    def build(self):
        with Router():
            with Vertical():
                with Routes():
                    with Route("/"):
                        Label("Home Content", id="home-label")
                    with Route("/other"):
                        Label("Other Content", id="other-label")
                Link("/other", "Go to Other", id="nav-btn")

@pytest.mark.asyncio
async def test_routing_navigation():
    app = App(SimpleRouterApp())
    async with app.run_test(size=(80, 24)) as pilot:
        # Give it a moment to layout
        await pilot.pause()
        
        # Initial route is "/"
        assert len(app.screen.query("#home-label")) == 1
        assert len(app.screen.query("#other-label")) == 0
        
        # Click navigate button
        app.screen.query_one("#nav-btn").focus()
        await pilot.press("enter")
        await pilot.pause()
        
        # Should be on "/other" now
        assert len(app.screen.query("#home-label")) == 0
        assert len(app.screen.query("#other-label")) == 1

class ManualNav(Component):
    def build(self):
        navigate = useNavigate()
        with Router():
            with Routes():
                with Route("/"):
                    Label("Home")
                with Route("/target"):
                    Label("Target", id="target")
            # Navigate manually via hook
            def trigger_nav():
                navigate("/target")
            
            # This is a bit tricky since useNavigate needs RouterContext
            # But here it's OUTSIDE Router? No, it's inside build of ManualNav
            # which is parent of Router.
            # So useNavigate() will FAIL here because it's not inside Router.
            Label("I will fail if I call useNavigate here")

@pytest.mark.asyncio
async def test_router_nested_navigation():
    class InternalNav(Component):
        def build(self):
            nav = useNavigate()
            Label("Nav", id="trigger")
            # We'll use a property to trigger navigation from test
            self.nav = nav

    class NestedApp(Component):
        def build(self):
            with Router():
                with Routes():
                    with Route("/"):
                        InternalNav(id="nav-comp")
                    with Route("/done"):
                        Label("Done", id="done")

    app = App(NestedApp())
    async with app.run_test() as pilot:
        assert len(app.screen.query("#done")) == 0
        
        nav_comp = app.screen.query_one("#nav-comp")
        # Trigger navigation programmatically
        nav_comp.nav("/done")
        await pilot.pause()
        
        assert len(app.screen.query("#done")) == 1

@pytest.mark.asyncio
async def test_dynamic_routing():
    class Profile(Component):
        def build(self):
            params = useParams()
            # We use content matching instead of ID to avoid DuplicateIds if re-render overlaps
            Label(f"User: {params.get('id')}")

    class DynamicApp(Component):
        def build(self):
            with Router():
                with Vertical():
                    with Routes():
                        with Route("/user/:id"):
                            Profile()
                    Link("/user/123", "User 123", id="link-123")
                    Link("/user/abc", "User ABC", id="link-abc")

    app = App(DynamicApp())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        app.screen.query_one("#link-123").focus()
        await pilot.press("enter")
        await pilot.pause()
        # Add an extra pause to allow all re-renders to settle
        await pilot.pause()
        assert app.screen.query_one(TextualLabel, expect_type=TextualLabel).content == "User: 123"
        
        app.screen.query_one("#link-abc").focus()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert app.screen.query_one(TextualLabel, expect_type=TextualLabel).content == "User: abc"

@pytest.mark.asyncio
async def test_dialog_route():
    class UserDetail(Component):
        def build(self):
            params = useParams()
            close = useCloseDialog()
            with Vertical():
                Label(f"Detail: {params.get('id')}", id="detail-label")
                Link("/", "Close", id="close-link")

    class DialogApp(Component):
        def build(self):
            with Router():
                with Vertical():
                    with Routes():
                        with Route("/"):
                            Label("Home List", id="home-label")
                    with DialogOutlet():
                        with DialogRoute("/user/:id"):
                            UserDetail()
                    Link("/user/42", "Open detail", dialog=True, id="open-link")

    app = App(DialogApp())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        # Dialog closed initially, background visible, no detail content.
        assert len(app.screen.query("#home-label")) == 1
        assert len(app.screen.query("#detail-label")) == 0

        # Open the dialog route.
        app.screen.query_one("#open-link").focus()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        # Background stays mounted, dialog content appears with params.
        assert len(app.screen.query("#home-label")) == 1
        assert app.screen.query_one("#detail-label", expect_type=TextualLabel).content == "Detail: 42"

        # Closing the dialog (via Link navigating back to "/") removes it
        # but keeps the background route intact.
        app.screen.query_one("#close-link").focus()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        assert len(app.screen.query("#home-label")) == 1
        assert len(app.screen.query("#detail-label")) == 0

@pytest.mark.asyncio
async def test_dialog_route_escape_closes():
    class UserDetail(Component):
        def build(self):
            params = useParams()
            Label(f"Detail: {params.get('id')}", id="detail-label")

    class DialogApp(Component):
        def build(self):
            with Router():
                with Vertical():
                    with Routes():
                        with Route("/"):
                            Label("Home List", id="home-label")
                    with DialogOutlet():
                        with DialogRoute("/user/:id"):
                            UserDetail()
                    Link("/user/42", "Open detail", dialog=True, id="open-link")

    app = App(DialogApp())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        app.screen.query_one("#open-link").focus()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert len(app.screen.query("#detail-label")) == 1

        await pilot.press("escape")
        await pilot.pause()
        await pilot.pause()

        assert len(app.screen.query("#detail-label")) == 0
        assert len(app.screen.query("#home-label")) == 1
