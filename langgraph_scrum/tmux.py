import libtmux
import os
import shutil
from typing import Optional, List

class TmuxManager:
    def __init__(self, session_name: str = "scrum-agents"):
        self.session_name = session_name
        self.server = libtmux.Server()
        self.session = self.ensure_session()

    def ensure_session(self) -> libtmux.Session:
        """Ensure the tmux session exists."""
        try:
            # Use iteration to find session by name
            session = None
            for s in self.server.sessions:
                if s.session_name == self.session_name:
                    session = s
                    break
            
            if not session:
                session = self.server.new_session(session_name=self.session_name, detach=True)
                print(f"[Tmux] Created new session: {self.session_name}")
            else:
                print(f"[Tmux] Found existing session: {self.session_name}")
            return session
        except Exception as e:
            print(f"[Tmux] Error ensuring session: {e}")
            raise

    def get_or_create_window(self, window_name: str) -> libtmux.Window:
        """Get a window by name or create it if it doesn't exist."""
        window = None
        for w in self.session.windows:
            if w.window_name == window_name:
                window = w
                break
                
        if not window:
            window = self.session.new_window(window_name=window_name, attach=False)
            print(f"[Tmux] Created window: {window_name}")
        return window

    def get_pane(self, window_name: str) -> Optional[libtmux.Pane]:
        """Get the first pane of a window."""
        window = self.get_or_create_window(window_name)
        if window:
            return window.panes[0]
        return None

    def send_keys(self, window_name: str, cmd: str, enter: bool = True):
        """Send keys/commands to a specific window's pane."""
        pane = self.get_pane(window_name)
        if pane:
            pane.send_keys(cmd, enter=enter)

    def read_pane(self, window_name: str, lines: int = 50) -> List[str]:
        """Read the last N lines from a pane."""
        pane = self.get_pane(window_name)
        if pane:
            # capture_pane returns a list of strings (lines) or a single string depending on version/args.
            # We treat it as list of lines. 
            # Note: start=-lines reads the last 'lines' lines.
            return pane.capture_pane(start=-lines)
        return []

    def load_layout(self, agent_roles: List[str]):
        """Pre-create windows for all expected agents."""
        for role in agent_roles:
            self.get_or_create_window(role)

# Global instance pattern for simplicity in this prototype
_tmux_manager_instance = None

def get_tmux_manager(session_name: str = "scrum-agents") -> TmuxManager:
    global _tmux_manager_instance
    if _tmux_manager_instance is None:
        _tmux_manager_instance = TmuxManager(session_name)
    return _tmux_manager_instance
