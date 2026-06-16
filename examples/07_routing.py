from pytui_react import Component, Router, Routes, Route, Link, Label, Vertical, Horizontal, Header, Footer, run, useLocation

class Home(Component):
    def build(self):
        with Vertical():
            Label("Welcome to the Home Screen!", styles={"background": "blue", "padding": 1})
            Label("Use the links below to navigate.")

class About(Component):
    def build(self):
        with Vertical():
            Label("About this Library", styles={"background": "green", "padding": 1})
            Label("pytui-react brings React-style components to Textual.")

class Settings(Component):
    def build(self):
        with Vertical():
            Label("Settings Screen", styles={"background": "red", "padding": 1})
            Label("Here you could configure your app.")

class Navbar(Component):
    def build(self):
        location = useLocation()
        with Horizontal(styles={"height": 3, "background": "grey", "border": ("solid", "white")}):
            Link("/", "Home", styles={"background": "blue" if location == "/" else "transparent"})
            Link("/about", "About", styles={"background": "blue" if location == "/about" else "transparent"})
            Link("/settings", "Settings", styles={"background": "blue" if location == "/settings" else "transparent"})

class MainApp(Component):
    def build(self):
        with Router():
            Header()
            Navbar()
            with Vertical(styles={"padding": 1}):
                with Routes():
                    with Route("/"):
                        Home()
                    with Route("/about"):
                        About()
                    with Route("/settings"):
                        Settings()
            Footer()

if __name__ == "__main__":
    run(MainApp())
