from __future__ import annotations
from typing import Any, Callable, Optional, List, Dict
from .hooks import createContext, useContext, useState, get_current_component
from .base import Component, register_widget
from .widgets import ContextProvider, Button, Dialog

RouterContext = createContext({
    "path": "/",
    "dialog_path": None,
    "navigate": lambda p, dialog=False: None,
    "close_dialog": lambda: None,
})
ParamsContext = createContext({})

def match_path(pattern: str, path: str) -> Optional[Dict[str, str]]:
    """Matches a path against a pattern and returns params if successful."""
    if pattern == path:
        return {}
        
    pattern_parts = [p for p in pattern.split("/") if p]
    path_parts = [p for p in path.split("/") if p]
    
    if not pattern_parts and not path_parts:
        return {}
        
    if not pattern_parts or len(pattern_parts) > len(path_parts):
        return None
    
    params = {}
    for i, p_part in enumerate(pattern_parts):
        if p_part.startswith(":"):
            # If it's the last part of the pattern, it can capture the rest
            if i == len(pattern_parts) - 1:
                params[p_part[1:]] = "/".join(path_parts[i:])
            else:
                params[p_part[1:]] = path_parts[i]
        elif p_part != path_parts[i]:
            return None
            
    # If there are remaining path parts but we finished the pattern 
    # and the last pattern part wasn't a parameter, it shouldn't match.
    if len(path_parts) > len(pattern_parts) and not pattern_parts[-1].startswith(":"):
        return None
        
    return params

class Router(Component):
    """Provides navigation state to the component tree."""
    can_focus = False
    def __init__(self, initial_path: str = "/", **kwargs):
        super().__init__(**kwargs)
        self.initial_path = initial_path

    def build(self):
        path, set_path = useState(self.initial_path)
        dialog_path, set_dialog_path = useState(None)

        def navigate(new_path: str, dialog: bool = False) -> None:
            if dialog:
                set_dialog_path(new_path)
            else:
                set_dialog_path(None)
                set_path(new_path)

        def close_dialog() -> None:
            set_dialog_path(None)

        with ContextProvider(RouterContext, {
            "path": path,
            "dialog_path": dialog_path,
            "navigate": navigate,
            "close_dialog": close_dialog,
        }):
            self.render_children()

class Routes(Component):
    """Renders the first child Route that matches the current path."""
    can_focus = False
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
    can_focus = False
    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def build(self):
        self.render_children()

class DialogRoute(Route):
    """A route that, when matched against the router's dialog location,
    renders its content inside a modal overlay instead of replacing the page."""
    pass

class DialogOutlet(Component):
    """Renders the first child DialogRoute matching the current dialog path
    inside a modal Dialog overlay. Place it anywhere inside a Router."""
    can_focus = False

    def build(self):
        context = useContext(RouterContext)
        dialog_path = context.get("dialog_path")
        close_dialog = context.get("close_dialog", lambda: None)

        if not dialog_path:
            return

        for child in self._children_builder.widgets:
            if hasattr(child, "path"):
                params = match_path(child.path, dialog_path)
                if params is not None:
                    child._route_params = params
                    with ContextProvider(ParamsContext, params):
                        with Dialog(on_close=close_dialog):
                            register_widget(child)
                    return

class Link(Component):
    """A button-like component that navigates to a specific path."""
    can_focus = True

    def __init__(self, to: str, label: str, dialog: bool = False, styles: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.label = label
        self.dialog = dialog
        self.styles_dict = styles
        self.styles.height = 1
        self._navigate_fn = None

    def build(self):
        navigate = useNavigate()
        self._navigate_fn = navigate
        Button(self.label, on_click=lambda: navigate(self.to, dialog=self.dialog), styles=self.styles_dict)

    def on_key(self, event) -> None:
        super().on_key(event)
        if event.key == "enter" and self._navigate_fn is not None:
            self._navigate_fn(self.to, dialog=self.dialog)
            event.stop()

def useNavigate() -> Callable[[str], None]:
    """Hook to get the navigation function."""
    context = useContext(RouterContext)
    return context.get("navigate", lambda p: None)

def useLocation() -> str:
    """Hook to get the current path."""
    context = useContext(RouterContext)
    return context.get("path", "/")

def useCloseDialog() -> Callable[[], None]:
    """Hook to get the function that closes the currently open dialog route."""
    context = useContext(RouterContext)
    return context.get("close_dialog", lambda: None)

def useParams() -> Dict[str, str]:
    """Hook to get the route parameters."""
    # Try direct injection from Routes/Route first
    comp = get_current_component()
    if hasattr(comp, "_route_params"):
        return comp._route_params
    
    # Fallback to parent walk (via useContext)
    return useContext(ParamsContext)
