#!/usr/bin/env python3
"""
Claude Code Telegram Monitor Bot - Entry Point

Usage:
    python run_bot.py

Before running:
    1. Copy .env.example to .env
    2. Add your TELEGRAM_BOT_TOKEN (from @BotFather)
    3. Add your TELEGRAM_CHAT_ID (from /start command)
    4. Install dependencies: pip install -r requirements.txt
"""
from bot.telegram_bot import run_bot

if __name__ == "__main__":
    run_bot()
