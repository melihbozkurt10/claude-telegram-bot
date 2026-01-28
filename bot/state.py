"""Session state management for Claude Code monitoring"""
import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .config import Config


@dataclass
class ToolExecution:
    """Represents a single tool execution"""
    tool_name: str
    tool_input: dict
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


@dataclass
class SessionState:
    """Current session state"""
    session_id: str = ""
    project_dir: str = ""
    start_time: float = 0.0
    end_time: Optional[float] = None
    is_active: bool = False
    total_tools: int = 0
    successful_tools: int = 0
    failed_tools: int = 0
    current_tool: Optional[dict] = None
    recent_tools: list = field(default_factory=list)
    last_update: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(**data)

    @property
    def duration_str(self) -> str:
        """Get human-readable session duration"""
        if self.start_time == 0:
            return "N/A"
        end = self.end_time or time.time()
        duration = int(end - self.start_time)

        if duration < 60:
            return f"{duration}s"
        elif duration < 3600:
            mins = duration // 60
            secs = duration % 60
            return f"{mins}m {secs}s"
        else:
            hours = duration // 3600
            mins = (duration % 3600) // 60
            return f"{hours}h {mins}m"


class StateManager:
    """Manages session state persistence"""

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or Config.STATE_FILE
        Config.ensure_dirs()

    def load(self) -> SessionState:
        """Load state from file"""
        if not self.state_file.exists():
            return SessionState()

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except (json.JSONDecodeError, TypeError):
            return SessionState()

    def save(self, state: SessionState) -> None:
        """Save state to file"""
        state.last_update = time.time()
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, default=str)

    def start_session(self, session_id: str, project_dir: str) -> SessionState:
        """Initialize a new session"""
        state = SessionState(
            session_id=session_id,
            project_dir=project_dir,
            start_time=time.time(),
            is_active=True,
            total_tools=0,
            successful_tools=0,
            failed_tools=0,
            recent_tools=[]
        )
        self.save(state)
        return state

    def end_session(self, reason: str = "completed") -> SessionState:
        """End the current session"""
        state = self.load()
        state.is_active = False
        state.end_time = time.time()
        state.current_tool = None
        self.save(state)
        return state

    def start_tool(self, tool_name: str, tool_input: dict) -> SessionState:
        """Record tool execution start"""
        state = self.load()
        state.current_tool = {
            "name": tool_name,
            "input": tool_input,
            "start_time": time.time()
        }
        self.save(state)
        return state

    def end_tool(self, tool_name: str, success: bool, output: str = "") -> SessionState:
        """Record tool execution end"""
        state = self.load()
        state.total_tools += 1

        if success:
            state.successful_tools += 1
        else:
            state.failed_tools += 1

        # Add to recent tools (keep last 10)
        tool_record = {
            "name": tool_name,
            "success": success,
            "time": datetime.now().strftime("%H:%M:%S"),
            "output": output[:100] if output else ""
        }
        state.recent_tools.append(tool_record)
        state.recent_tools = state.recent_tools[-10:]

        state.current_tool = None
        self.save(state)
        return state

    def get_status_summary(self) -> str:
        """Get formatted status summary for Telegram"""
        state = self.load()

        if not state.session_id:
            return "No active session"

        status_icon = "Active" if state.is_active else "Ended"

        lines = [
            f"Session: {state.session_id[:8]}",
            f"Project: {Path(state.project_dir).name if state.project_dir else 'N/A'}",
            f"Status: {status_icon}",
            f"Duration: {state.duration_str}",
            f"Tools: {state.successful_tools}/{state.total_tools}",
            f"Errors: {state.failed_tools}",
        ]

        if state.current_tool:
            lines.append(f"Current: {state.current_tool['name']}")

        return "\n".join(lines)
