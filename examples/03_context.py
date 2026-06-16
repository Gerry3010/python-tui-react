from pytui_react import (
    Component, Label, Button, Vertical, Horizontal, 
    useState, useContext, createContext, ContextProvider, run
)

# Create a theme context
ThemeContext = createContext({"bg": "black", "fg": "white", "name": "Light"})

class ThemeSwitcher(Component):
    def build(self):
        theme, set_theme = useState("light")
        
        current_theme = {
            "bg": "white" if theme == "light" else "black",
            "fg": "black" if theme == "light" else "white",
            "name": theme.capitalize()
        }
        
        with ContextProvider(ThemeContext, current_theme):
            with Vertical(styles={"background": current_theme["bg"], "color": current_theme["fg"]}):
                Label(f"Active Theme: [bold]{current_theme['name']}[/]")
                Button("Toggle Theme", 
                       on_click=lambda: set_theme("dark" if theme == "light" else "light"))
                
                # A nested component that consumes context
                ThemedInfo()

class ThemedInfo(Component):
    def build(self):
        theme = useContext(ThemeContext)
        with Vertical(styles={"border": ("double", theme["fg"]), "margin": (1, 0), "padding": (1, 1)}):
            Label("I am a nested component consuming the theme context.")
            Label(f"My background is {theme['bg']} and foreground is {theme['fg']}.")

if __name__ == "__main__":
    run(ThemeSwitcher())
