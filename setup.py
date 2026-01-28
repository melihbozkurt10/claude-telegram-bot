#!/usr/bin/env python3
"""
Setup script for Claude Code Telegram Monitor Bot

This script helps you:
1. Install dependencies
2. Create .env file from template
3. Get your Telegram Chat ID
4. Configure Claude Code hooks
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}\n")


def print_step(step: int, text: str) -> None:
    """Print a step indicator"""
    print(f"[{step}] {text}")


def check_python_version() -> bool:
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print(f"Error: Python 3.9+ required. You have {sys.version}")
        return False
    print(f"Python version: {sys.version}")
    return True


def install_dependencies() -> bool:
    """Install required packages"""
    print_header("Installing Dependencies")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\nDependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        return False


def setup_env_file() -> bool:
    """Create .env file from template"""
    print_header("Setting Up Environment")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print(".env file already exists")
        overwrite = input("Overwrite? (y/N): ").lower().strip()
        if overwrite != "y":
            return True

    if not env_example.exists():
        print("Error: .env.example not found")
        return False

    shutil.copy(env_example, env_file)
    print(".env file created from template")

    print("\n" + "-"*40)
    print("Now you need to configure your .env file:")
    print("-"*40)
    print_step(1, "Open Telegram and search for @BotFather")
    print_step(2, "Send /newbot and follow the instructions")
    print_step(3, "Copy the token and add it to .env:")
    print("       TELEGRAM_BOT_TOKEN=your_token_here")
    print()
    print_step(4, "Run the bot: python run_bot.py")
    print_step(5, "Send /start to your bot in Telegram")
    print_step(6, "Copy the Chat ID and add it to .env:")
    print("       TELEGRAM_CHAT_ID=your_chat_id_here")
    print("-"*40)

    return True


def setup_claude_hooks() -> None:
    """Show Claude Code hook setup instructions"""
    print_header("Claude Code Hook Setup")

    project_dir = Path.cwd()
    claude_settings = project_dir / ".claude" / "settings.json"

    if claude_settings.exists():
        print("Claude Code hooks are already configured!")
        print(f"Settings file: {claude_settings}")
    else:
        print("Warning: .claude/settings.json not found")
        print("Make sure you're running this from the project directory")

    print("\nTo enable monitoring in other projects, run:")
    print("  python install_hooks.py")


def main():
    """Main setup flow"""
    print_header("Claude Code Telegram Monitor - Setup")

    if not check_python_version():
        return 1

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Install dependencies
    if not install_dependencies():
        return 1

    # Setup .env
    if not setup_env_file():
        return 1

    # Show hook setup
    setup_claude_hooks()

    print_header("Setup Complete!")
    print("Next steps:")
    print("  1. Configure your .env file with Telegram credentials")
    print("  2. Run the bot: python run_bot.py")
    print("  3. Test with /start command in Telegram")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
