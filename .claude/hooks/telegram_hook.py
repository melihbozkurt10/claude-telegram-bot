#!/usr/bin/env python3
"""
Claude Code Hook Handler - Sends notifications to Telegram
This script is called by Claude Code hooks and receives JSON via stdin.
"""
import json
import sys
import os
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
PROJECT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from bot.config import Config
from bot.state import StateManager


def send_telegram_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send message to Telegram using urllib (no external dependencies)"""
    if not Config.BOT_TOKEN or not Config.CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": Config.CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)
        return False


def format_command(tool_input: dict) -> str:
    """Format command for display"""
    if "command" in tool_input:
        cmd = tool_input["command"]
        return cmd[:80] + "..." if len(cmd) > 80 else cmd
    return str(tool_input)[:80]


def handle_session_start(data: dict, state_manager: StateManager) -> None:
    """Handle SessionStart event"""
    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", "")

    state_manager.start_session(session_id, cwd)

    project_name = Path(cwd).name if cwd else "Unknown"
    message = f"""<b>SESSION STARTED</b>
<b>Session:</b> <code>{session_id[:8]}</code>
<b>Project:</b> {project_name}
<b>Time:</b> {datetime.now().strftime("%H:%M:%S")}"""

    send_telegram_message(message)


def handle_session_end(data: dict, state_manager: StateManager) -> None:
    """Handle SessionEnd event"""
    reason = data.get("reason", "completed")
    state = state_manager.end_session(reason)

    message = f"""<b>SESSION ENDED</b>
<b>Session:</b> <code>{state.session_id[:8]}</code>
<b>Duration:</b> {state.duration_str}
<b>Tools:</b> {state.successful_tools}/{state.total_tools}
<b>Errors:</b> {state.failed_tools}
<b>Reason:</b> {reason}"""

    send_telegram_message(message)


def handle_pre_tool_use(data: dict, state_manager: StateManager) -> None:
    """Handle PreToolUse event - update state, optionally notify"""
    tool_name = data.get("tool_name", "Unknown")
    tool_input = data.get("tool_input", {})

    state_manager.start_tool(tool_name, tool_input)

    # Only notify for Bash commands (most relevant for monitoring)
    if tool_name == "Bash" and Config.NOTIFY_ON_LONG_RUNNING:
        command = format_command(tool_input)
        message = f"""<b>RUNNING</b>
<b>Tool:</b> {tool_name}
<b>Command:</b> <code>{command}</code>
<b>Time:</b> {datetime.now().strftime("%H:%M:%S")}"""
        send_telegram_message(message)


def handle_post_tool_use(data: dict, state_manager: StateManager) -> None:
    """Handle PostToolUse event - tool completed successfully"""
    tool_name = data.get("tool_name", "Unknown")
    tool_response = data.get("tool_response", {})

    # Extract output info
    output = ""
    if isinstance(tool_response, dict):
        if "stdout" in tool_response:
            output = tool_response.get("stdout", "")[:100]
        elif "content" in tool_response:
            output = str(tool_response.get("content", ""))[:100]

    state_manager.end_tool(tool_name, success=True, output=output)

    # Notify for Bash completions
    if tool_name == "Bash" and Config.NOTIFY_ON_COMPLETE:
        exit_code = tool_response.get("exitCode", 0) if isinstance(tool_response, dict) else 0
        status = "SUCCESS" if exit_code == 0 else f"Exit: {exit_code}"

        message = f"""<b>COMPLETED</b>
<b>Tool:</b> {tool_name}
<b>Status:</b> {status}
<b>Time:</b> {datetime.now().strftime("%H:%M:%S")}"""

        if output:
            message += f"\n<b>Output:</b> <code>{output}</code>"

        send_telegram_message(message)


def handle_post_tool_use_failure(data: dict, state_manager: StateManager) -> None:
    """Handle PostToolUseFailure event - tool failed"""
    tool_name = data.get("tool_name", "Unknown")
    tool_input = data.get("tool_input", {})
    error = data.get("tool_response", {})

    # Extract error message
    error_msg = ""
    if isinstance(error, dict):
        error_msg = error.get("stderr", "") or error.get("error", "") or str(error)
    else:
        error_msg = str(error)
    error_msg = error_msg[:200]

    state_manager.end_tool(tool_name, success=False, output=error_msg)

    if Config.NOTIFY_ON_ERROR:
        command = format_command(tool_input)
        message = f"""<b>ERROR</b>
<b>Tool:</b> {tool_name}
<b>Command:</b> <code>{command}</code>
<b>Error:</b> <code>{error_msg}</code>
<b>Time:</b> {datetime.now().strftime("%H:%M:%S")}"""

        send_telegram_message(message)


def main():
    """Main hook handler entry point"""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Silently exit on invalid JSON

    hook_event = input_data.get("hook_event_name", "")
    state_manager = StateManager()

    # Route to appropriate handler
    handlers = {
        "SessionStart": handle_session_start,
        "SessionEnd": handle_session_end,
        "PreToolUse": handle_pre_tool_use,
        "PostToolUse": handle_post_tool_use,
        "PostToolUseFailure": handle_post_tool_use_failure,
    }

    handler = handlers.get(hook_event)
    if handler:
        handler(input_data, state_manager)

    # Always exit successfully to not block Claude
    sys.exit(0)


if __name__ == "__main__":
    main()
