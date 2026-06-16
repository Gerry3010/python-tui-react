from pytui_react import (
    Component, Router, Routes, Route, DialogRoute, DialogOutlet, Link,
    Label, Vertical, Header, Footer, run, useParams,
)

USERS = ["alice", "bob", "charlie"]

class UserDetailDialog(Component):
    def build(self):
        params = useParams()
        user_id = params.get("id", "Unknown")
        with Vertical():
            Label(f"User Detail: {user_id}", styles={"bold": True})
            Label("Press Escape or click 'Close' to dismiss.")
            Link("/", "Close")

class UserList(Component):
    def build(self):
        with Vertical():
            Label("Select a user to view details in a dialog:", styles={"bold": True})
            for user in USERS:
                Link(f"/user/{user}", f"View {user.capitalize()}", dialog=True)

class AppContent(Component):
    def build(self):
        with Vertical():
            Header()
            with Vertical(styles={"padding": 1}):
                with Routes():
                    with Route("/"):
                        UserList()
                with DialogOutlet():
                    with DialogRoute("/user/:id"):
                        UserDetailDialog()
            Footer()

class MainApp(Component):
    def build(self):
        with Router():
            AppContent()

if __name__ == "__main__":
    run(MainApp())
