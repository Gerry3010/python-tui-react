from __future__ import annotations
from typing import Any, Callable, List, Optional, Tuple, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .base import Component
    from textual.app import App as TextualApp

from textual.binding import Binding

class HookState:
    def __init__(self, value: Any):
        self.value = value

class EffectState:
    def __init__(self, deps: Optional[List[Any]], cleanup: Optional[Callable] = None):
        self.deps = deps
        self.cleanup = cleanup

def get_current_component() -> Component:
    from .base import UIBuilder
    comp = UIBuilder.get_current_component()
    if comp is None:
        raise RuntimeError("Hooks must be called inside a Component.build() method")
    return comp

def useState(initial_value: Any) -> Tuple[Any, Callable[[Any], None]]:
    comp = get_current_component()
    
    if not hasattr(comp, "_hooks"):
        comp._hooks = []
    if not hasattr(comp, "_hook_index"):
        comp._hook_index = 0
        
    idx = comp._hook_index
    comp._hook_index += 1
    
    if len(comp._hooks) <= idx:
        comp._hooks.append(HookState(initial_value))
    
    state = comp._hooks[idx]
    
    def set_state(new_value: Any) -> None:
        if callable(new_value):
            state.value = new_value(state.value)
        else:
            state.value = new_value
        comp.re_render()
        
    return state.value, set_state

def useEffect(callback: Callable[[], Optional[Callable]], deps: Optional[List[Any]] = None) -> None:
    comp = get_current_component()
    
    if not hasattr(comp, "_hooks"):
        comp._hooks = []
    if not hasattr(comp, "_hook_index"):
        comp._hook_index = 0
        
    idx = comp._hook_index
    comp._hook_index += 1
    
    if len(comp._hooks) <= idx:
        state = EffectState(deps)
        comp._hooks.append(state)
        _schedule_effect(comp, idx, callback)
    else:
        state = comp._hooks[idx]
        if _deps_changed(state.deps, deps):
            state.deps = deps
            _schedule_effect(comp, idx, callback)

def _deps_changed(old_deps: Optional[List[Any]], new_deps: Optional[List[Any]]) -> bool:
    if old_deps is None or new_deps is None:
        return True
    if len(old_deps) != len(new_deps):
        return True
    return any(o != n for o, n in zip(old_deps, new_deps))

def _schedule_effect(comp: Component, idx: int, callback: Callable) -> None:
    def effect_task():
        state = comp._hooks[idx]
        if state.cleanup:
            try:
                state.cleanup()
            except Exception:
                pass # TODO: Log error
        state.cleanup = callback()
    
    # Use call_after_refresh to ensure it runs after Textual has updated the DOM
    comp.call_after_refresh(effect_task)

def useContext(context: Any) -> Any:
    from .base import UIBuilder
    comp = UIBuilder.get_current_component()
    
    # 1. Check current build-time stack (for synchronous nesting)
    val = UIBuilder.get_context_value(context)
    if val is not getattr(context, "default_value", None):
        return val

    # 2. Check widget parent chain (for async re-renders)
    if comp:
        curr = comp.parent
        while curr:
            # We look for a widget that has 'context' and 'value' attributes 
            # (matches ContextProvider in widgets.py)
            if hasattr(curr, "context") and getattr(curr, "context") == context:
                return getattr(curr, "value")
            curr = curr.parent

    return getattr(context, "default_value", None)

class Context:
    def __init__(self, default_value: Any):
        self.default_value = default_value

def createContext(default_value: Any) -> Context:
    return Context(default_value)

def useApp() -> TextualApp:
    """Returns the current Textual App instance."""
    comp = get_current_component()
    return comp.app

def useInterval(callback: Callable, interval: float, deps: Optional[List[Any]] = None) -> None:
    """Runs a callback at regular intervals."""
    comp = get_current_component()
    
    def effect():
        timer = comp.set_interval(interval, callback)
        return lambda: timer.stop()
    
    useEffect(effect, deps if deps is not None else [interval])

def useTimeout(callback: Callable, delay: float, deps: Optional[List[Any]] = None) -> None:
    """Runs a callback after a delay."""
    comp = get_current_component()
    
    def effect():
        timer = comp.set_timer(delay, callback)
        return lambda: timer.stop()
    
    useEffect(effect, deps if deps is not None else [delay])

def useKey(key: str, callback: Callable, description: Optional[str] = None, show: bool = True, global_key: bool = False) -> None:
    """Registers a callback for a specific key press. 
    
    If description is provided, it registers a binding that will be displayed in the Footer.
    If global_key is True, the binding is registered on the App level.
    """
    comp = get_current_component()
    target = comp.app if global_key else comp

    if not hasattr(target, "_key_handlers"):
        target._key_handlers = {}

    def effect():
        if description:
            # Use Textual's binding system
            action_id = f"k_{key}_{id(callback)}"
            
            # Ensure the target has binding storage
            if not hasattr(target, "_binding_handlers"):
                target._binding_handlers = {}
            target._binding_handlers[action_id] = callback
            
            if hasattr(target, "bind"):
                target.bind(key, f"hook_dispatch('{action_id}')", description=description, show=show)
            else:
                # Fallback
                binding = Binding(key, f"hook_dispatch('{action_id}')", description, show=show)
                if hasattr(target, "_bindings"):
                    target._bindings._add_binding(binding)
            
            # Try to refresh bindings
            try:
                if hasattr(comp.app, "refresh_bindings"):
                    comp.app.refresh_bindings()
            except Exception:
                pass

            def cleanup():
                if hasattr(target, "_binding_handlers"):
                    target._binding_handlers.pop(action_id, None)
                _unbind(target, key)
                try:
                    if hasattr(comp.app, "refresh_bindings"):
                        comp.app.refresh_bindings()
                except Exception:
                    pass
            return cleanup
        else:
            target._key_handlers[key] = callback
            return lambda: target._key_handlers.pop(key, None)
    
    useEffect(effect, [key, description, show, global_key])

def _unbind(comp: Any, key: str) -> None:
    """Helper to remove a binding from a Textual component."""
    if hasattr(comp, "_bindings") and key in comp._bindings.key_to_bindings:
        del comp._bindings.key_to_bindings[key]

def useFocus() -> Tuple[bool, Callable[[], None]]:
    """Manages focus state for the component."""
    comp = get_current_component()
    focused, set_focused = useState(comp.has_focus)
    
    if not hasattr(comp, "_focus_handlers"):
        comp._focus_handlers = set()
    
    def effect():
        comp._focus_handlers.add(set_focused)
        return lambda: comp._focus_handlers.remove(set_focused)
    
    useEffect(effect, [])
    
    return focused, lambda: comp.focus()
