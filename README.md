# Claude Code Telegram Monitor Bot

Monitor Claude Code sessions from your phone via Telegram:
- Session started/ended notifications
- Command execution alerts
- Error notifications

## Installation

### 1. Create Telegram Bot

1. Open [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. **Copy the token**

### 2. Setup Project

```bash
# Clone
git clone https://github.com/USER/claude-telegram-bot.git
cd claude-telegram-bot

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 3. Add Token

Edit `.env` and add your token:
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
```

### 4. Get Chat ID

```bash
python run_bot.py
```

While the bot is running, send `/start` to your bot on Telegram. Copy the Chat ID and add it to `.env`:
```
TELEGRAM_CHAT_ID=123456789
```

### 5. Enable Hooks

**Option A: This project only** (when working in project directory)
```bash
# .claude/settings.json is already configured, works automatically
```

**Option B: All projects** (global)
```bash
python install_hooks.py
```

### 6. Test

Open a new terminal and start Claude Code:
```bash
claude
```

Run a bash command - you should receive a Telegram notification!

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show your Chat ID |
| `/status` | Current status |
| `/session` | Session details |
| `/tasks` | Recent operations |
| `/help` | Help |

## Project Structure

```
claude-telegram-bot/
├── .claude/
│   ├── settings.json        # Hook configuration
│   └── hooks/
│       └── telegram_hook.py # Hook handler
├── bot/
│   ├── config.py            # Configuration
│   ├── state.py             # Session state
│   └── telegram_bot.py      # Bot service
├── .env                     # Credentials (gitignored)
├── .env.example             # Template
├── requirements.txt
├── run_bot.py               # Start bot
├── install_hooks.py         # Global hook installer
└── README.md
```

## Notification Settings

In `.env`:

```env
NOTIFY_ON_ERROR=true          # Notify on errors
NOTIFY_ON_COMPLETE=true       # Notify on completion
NOTIFY_ON_LONG_RUNNING=true   # Notify on long operations
LONG_RUNNING_THRESHOLD=30     # Seconds before "long running"
```

## License

MIT
