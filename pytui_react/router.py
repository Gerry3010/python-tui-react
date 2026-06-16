from __future__ import annotations
from typing import Any, Callable, Optional, List, Dict
from .hooks import createContext, useContext, useState, get_current_component
from .base import Component, register_widget
from .widgets import ContextProvider, Button

RouterContext = createContext({"path": "/", "navigate": lambda p: None})
ParamsContext = createContext({})

def match_path(pattern: str, path: str) -> Optional[Dict[str, str]]:
    """Matches a path against a pattern and returns params if successful."""
    if pattern == path:
        return {}
        
    # Handle root path specially if needed, but strip().split() handles it
    pattern_parts = [p for p in pattern.split("/") if p]
    path_parts = [p for p in path.split("/") if p]
    
    if len(pattern_parts) != len(path_parts):
        return None
    
    params = {}
    for p_part, path_part in zip(pattern_parts, path_parts):
        if p_part.startswith(":"):
            params[p_part[1:]] = path_part
        elif p_part != path_part:
            return None
    return params

class Router(Component):
    """Provides navigation state to the component tree."""
    def __init__(self, initial_path: str = "/", **kwargs):
        super().__init__(**kwargs)
        self.initial_path = initial_path

    def build(self):
        path, set_path = useState(self.initial_path)
        
        def navigate(new_path: str) -> None:
            set_path(new_path)
            
        with ContextProvider(RouterContext, {"path": path, "navigate": navigate}):
            self.render_children()

class Routes(Component):
    """Renders the first child Route that matches the current path."""
    def build(self):
        context = useContext(RouterContext)
        current_path = context.get("path", "/")
        
        for child in self._children_builder.widgets:
            if hasattr(child, "path"):
                params = match_path(child.path, current_path)
                if params is not None:
                    child._route_params = params
                    with ContextProvider(ParamsContext, params):
                        register_widget(child)
                    return

class Route(Component):
    """A single route definition."""
    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        
    def build(self):
        self.render_children()

class Link(Component):
    """A button-like component that navigates to a specific path."""
    can_focus = True

    def __init__(self, to: str, label: str, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.label = label
        self.styles_dict = styles
        self.styles.height = 1
        self._navigate_fn = None

    def build(self):
        navigate = useNavigate()
        self._navigate_fn = navigate
        Button(self.label, on_click=lambda: navigate(self.to), styles=self.styles_dict)

    def on_key(self, event) -> None:
        super().on_key(event)
        if event.key == "enter" and self._navigate_fn is not None:
            self._navigate_fn(self.to)
            event.stop()

def useNavigate() -> Callable[[str], None]:
    """Hook to get the navigation function."""
    context = useContext(RouterContext)
    return context.get("navigate", lambda p: None)

def useLocation() -> str:
    """Hook to get the current path."""
    context = useContext(RouterContext)
    return context.get("path", "/")

def useParams() -> Dict[str, str]:
    """Hook to get the route parameters."""
    # Try direct injection from Routes/Route first
    comp = get_current_component()
    if hasattr(comp, "_route_params"):
        return comp._route_params
    
    # Fallback to parent walk (via useContext)
    return useContext(ParamsContext)
