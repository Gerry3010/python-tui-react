from pytui_react import Component, Router, Routes, Route, Link, Label, Vertical, Horizontal, Header, Footer, run, useParams, useLocation

class UserProfile(Component):
    def build(self):
        params = useParams()
        user_id = params.get("id", "Unknown")
        
        with Vertical(styles={"padding": 1, "border": ("solid", "green")}):
            Label(f"User Profile", styles={"background": "green", "bold": True})
            Label(f"Viewing details for user ID: {user_id}")
            Link("/users", "Back to User List")

class UserList(Component):
    def build(self):
        users = ["alice", "bob", "charlie"]
        with Vertical():
            Label("Select a user:", styles={"bold": True})
            for user in users:
                Link(f"/user/{user}", f"View {user.capitalize()}'s Profile")

class AppContent(Component):
    def build(self):
        location = useLocation()
        with Vertical():
            Header()
            with Horizontal(styles={"height": 3, "background": "grey"}):
                Link("/", "Home", styles={"background": "blue" if location == "/" else "transparent"})
                Link("/users", "Users", styles={"background": "blue" if location.startswith("/user") else "transparent"})
            
            with Vertical(styles={"padding": 1}):
                with Routes():
                    with Route("/"):
                        Label("Welcome to the Dynamic Routing Example!")
                        Label("Click 'Users' to see dynamic segments in action.")
                    with Route("/users"):
                        UserList()
                    with Route("/user/:id"):
                        UserProfile()
            Footer()

class MainApp(Component):
    def build(self):
        with Router():
            AppContent()

if __name__ == "__main__":
    run(MainApp())
