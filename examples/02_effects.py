import asyncio
from pytui_react import Component, Label, Vertical, useState, useEffect, run

class Timer(Component):
    def build(self):
        count, set_count = useState(0)
        is_running, set_is_running = useState(True)
        
        # Effect hook to run a timer
        def timer_effect():
            if not is_running:
                return None
                
            async def run_timer():
                while is_running:
                    await asyncio.sleep(1)
                    set_count(lambda c: c + 1)
            
            # Start a background task using Textual's worker system
            worker = self.run_worker(run_timer(), thread=True)
            
            # Cleanup function to stop the timer
            def cleanup():
                worker.cancel()
                
            return cleanup
            
        useEffect(timer_effect, [is_running])
        
        with Vertical(styles={"align": ("center", "middle"), "background": "darkblue"}):
            Label(f"Time Elapsed: [bold yellow]{count}[/] seconds")
            Label(f"Status: {'[green]Running[/]' if is_running else '[red]Paused[/]'}")
            
            from pytui_react import Button
            Button("Pause" if is_running else "Resume", 
                   on_click=lambda: set_is_running(not is_running))

if __name__ == "__main__":
    run(Timer())
