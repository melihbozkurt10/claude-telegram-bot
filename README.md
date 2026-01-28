# Claude Code Telegram Monitor

> Real-time notifications for Claude Code sessions — monitor your AI coding assistant from anywhere.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai)

---

## Features

- **Real-time Notifications** — Get instant alerts when tasks complete or errors occur
- **Session Monitoring** — Track active sessions, tool executions, and error counts
- **Mobile Access** — Check status from your phone via Telegram commands
- **Zero Config** — Works automatically once installed, no manual intervention needed
- **Customizable** — Choose which events trigger notifications

## Preview

```
SESSION STARTED
Session: abc12345
Project: my-project
Time: 14:32:05

──────────────────────

COMPLETED
Tool: Bash
Status: SUCCESS
Time: 14:32:18
Output: Build successful

──────────────────────

ERROR
Tool: Bash
Command: npm test
Error: 3 tests failing
```

---

## Quick Start

### 1. Create Your Telegram Bot

1. Open [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the prompts
3. Save the **API token** you receive

### 2. Install

```bash
git clone https://github.com/YOUR_USERNAME/claude-telegram-bot.git
cd claude-telegram-bot
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Get your Chat ID:** Run `python run_bot.py`, then send `/start` to your bot on Telegram.

### 4. Enable Hooks

```bash
python install_hooks.py
```

### 5. Done

Start a new Claude Code session — notifications will flow to Telegram automatically.

---

## Usage

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and Chat ID |
| `/status` | Current Claude Code status |
| `/session` | Active session details |
| `/tasks` | Recent tool executions |
| `/help` | Show all commands |

### Notification Events

| Event | Trigger |
|-------|---------|
| Session Started | New Claude Code session begins |
| Session Ended | Session closes with summary |
| Running | Bash command starts |
| Completed | Bash command succeeds |
| Error | Any tool fails |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | *required* |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | *required* |
| `NOTIFY_ON_ERROR` | Send error notifications | `true` |
| `NOTIFY_ON_COMPLETE` | Send completion notifications | `true` |
| `NOTIFY_ON_LONG_RUNNING` | Alert on long operations | `true` |
| `LONG_RUNNING_THRESHOLD` | Seconds before "long running" | `30` |

### Hook Scope

**Project-level** (this project only):
- Hooks in `.claude/settings.json` activate when working in this directory

**Global** (all projects):
```bash
python install_hooks.py  # Install
python install_hooks.py  # Choose option 2 to uninstall
```

---

## Project Structure

```
claude-telegram-bot/
├── .claude/
│   ├── settings.json          # Hook configuration
│   └── hooks/
│       └── telegram_hook.py   # Event handler
├── bot/
│   ├── __init__.py
│   ├── config.py              # Environment config
│   ├── state.py               # Session state manager
│   └── telegram_bot.py        # Telegram bot service
├── state/                     # Runtime state files
├── .env.example               # Environment template
├── .gitignore
├── requirements.txt
├── run_bot.py                 # Bot entry point
├── install_hooks.py           # Global installer
├── setup.py                   # Interactive setup
└── README.md
```

---

## Troubleshooting

### Notifications not working?

1. **Check credentials** — Verify `.env` has correct token and chat ID
2. **Restart session** — Hooks load at session start, open a new terminal
3. **Test manually:**
   ```bash
   echo '{"hook_event_name": "SessionStart", "session_id": "test", "cwd": "/test"}' | python .claude/hooks/telegram_hook.py
   ```

### Bot not responding?

1. Make sure `python run_bot.py` is running
2. Check if you started a chat with your bot first
3. Verify the bot token is correct

---

## Contributing

Contributions welcome. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## License

MIT
