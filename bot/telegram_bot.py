"""Telegram Bot Service for Claude Code Monitoring"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from .config import Config
from .state import StateManager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize state manager
state_manager = StateManager()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show welcome message and chat ID"""
    chat_id = update.effective_chat.id
    user = update.effective_user

    message = f"""<b>Claude Code Monitor Bot</b>

Welcome {user.first_name}!

Your Chat ID: <code>{chat_id}</code>

Copy this Chat ID and add it to your <code>.env</code> file:
<code>TELEGRAM_CHAT_ID={chat_id}</code>

<b>Available Commands:</b>
/status - Current Claude Code status
/session - Active session details
/tasks - Recent tool executions
/help - Show this help message"""

    await update.message.reply_html(message)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - show current status"""
    state = state_manager.load()

    if not state.session_id:
        await update.message.reply_html("<b>No active session</b>\n\nClaude Code is not currently running.")
        return

    status_icon = "ACTIVE" if state.is_active else "IDLE"

    message = f"""<b>CLAUDE CODE STATUS</b>

<b>Status:</b> {status_icon}
<b>Session:</b> <code>{state.session_id[:8]}</code>
<b>Duration:</b> {state.duration_str}
<b>Tools Run:</b> {state.successful_tools}/{state.total_tools}
<b>Errors:</b> {state.failed_tools}"""

    if state.current_tool:
        tool_name = state.current_tool.get("name", "Unknown")
        message += f"\n\n<b>Currently Running:</b> {tool_name}"

    await update.message.reply_html(message)


async def session_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /session command - show session details"""
    state = state_manager.load()

    if not state.session_id:
        await update.message.reply_html("<b>No session data</b>")
        return

    from pathlib import Path
    project_name = Path(state.project_dir).name if state.project_dir else "Unknown"

    message = f"""<b>SESSION DETAILS</b>

<b>Session ID:</b> <code>{state.session_id}</code>
<b>Project:</b> {project_name}
<b>Status:</b> {"Active" if state.is_active else "Ended"}
<b>Duration:</b> {state.duration_str}

<b>Statistics:</b>
  Total Tools: {state.total_tools}
  Successful: {state.successful_tools}
  Failed: {state.failed_tools}"""

    await update.message.reply_html(message)


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tasks command - show recent tool executions"""
    state = state_manager.load()

    if not state.recent_tools:
        await update.message.reply_html("<b>No recent tasks</b>")
        return

    message = "<b>RECENT TASKS</b>\n\n"

    for tool in reversed(state.recent_tools[-5:]):
        icon = "OK" if tool.get("success", True) else "ERR"
        name = tool.get("name", "Unknown")
        time = tool.get("time", "")
        message += f"[{icon}] {name} - {time}\n"

    await update.message.reply_html(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    message = """<b>Claude Code Monitor Bot</b>

<b>Commands:</b>
/start - Welcome message and setup
/status - Current Claude Code status
/session - Active session details
/tasks - Recent tool executions
/help - This help message

<b>Notifications:</b>
You'll receive automatic notifications when:
- Session starts/ends
- Commands are executed
- Errors occur

<b>Setup:</b>
1. Copy your Chat ID from /start
2. Add it to .env file
3. Restart the bot"""

    await update.message.reply_html(message)


def create_bot() -> Application:
    """Create and configure the Telegram bot application"""
    is_valid, error = Config.validate()
    if not is_valid:
        raise ValueError(f"Configuration error: {error}")

    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("session", session_command))
    application.add_handler(CommandHandler("tasks", tasks_command))
    application.add_handler(CommandHandler("help", help_command))

    return application


def run_bot() -> None:
    """Run the Telegram bot"""
    logger.info("Starting Claude Code Monitor Bot...")

    try:
        app = create_bot()
        logger.info("Bot started successfully. Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except ValueError as e:
        logger.error(f"Failed to start bot: {e}")
        raise
