#!/usr/bin/env python3
"""
Install Claude Code hooks globally

This script adds Telegram notification hooks to your global Claude Code settings.
After running this, all Claude Code sessions will send notifications to Telegram.
"""
import json
import os
from pathlib import Path


def get_claude_settings_path() -> Path:
    """Get path to global Claude settings"""
    return Path.home() / ".claude" / "settings.json"


def get_hook_script_path() -> str:
    """Get absolute path to hook script"""
    script_dir = Path(__file__).parent.absolute()
    hook_path = script_dir / ".claude" / "hooks" / "telegram_hook.py"
    # Use forward slashes for cross-platform compatibility
    return str(hook_path).replace("\\", "/")


def create_hooks_config(hook_path: str) -> dict:
    """Create hooks configuration"""
    hook_command = f'python "{hook_path}"'

    return {
        "SessionStart": [
            {"hooks": [{"type": "command", "command": hook_command, "timeout": 15}]}
        ],
        "SessionEnd": [
            {"hooks": [{"type": "command", "command": hook_command, "timeout": 15}]}
        ],
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": hook_command, "timeout": 15}]}
        ],
        "PostToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": hook_command, "timeout": 15}]}
        ],
        "PostToolUseFailure": [
            {"matcher": "*", "hooks": [{"type": "command", "command": hook_command, "timeout": 15}]}
        ]
    }


def install_hooks() -> bool:
    """Install hooks to global Claude settings"""
    settings_path = get_claude_settings_path()
    hook_path = get_hook_script_path()

    print(f"Hook script: {hook_path}")
    print(f"Settings file: {settings_path}")

    # Load existing settings
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {}

    # Check if hooks already exist
    if "hooks" in settings:
        print("\nWarning: Existing hooks found!")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return False

    # Add hooks
    settings["hooks"] = create_hooks_config(hook_path)

    # Save settings
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    print("\nHooks installed successfully!")
    print("\nNext steps:")
    print("1. Make sure .env is configured with your Telegram credentials")
    print("2. Start a new Claude Code session")
    print("3. Run a bash command - you should get a Telegram notification!")

    return True


def uninstall_hooks() -> bool:
    """Remove hooks from global Claude settings"""
    settings_path = get_claude_settings_path()

    if not settings_path.exists():
        print("No settings file found.")
        return False

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    if "hooks" not in settings:
        print("No hooks found.")
        return False

    del settings["hooks"]

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    print("Hooks removed successfully!")
    return True


def main():
    print("=" * 50)
    print("  Claude Code Telegram Hooks Installer")
    print("=" * 50)
    print()
    print("1. Install hooks (enable Telegram notifications)")
    print("2. Uninstall hooks (disable notifications)")
    print("3. Cancel")
    print()

    choice = input("Choose (1/2/3): ").strip()

    if choice == "1":
        install_hooks()
    elif choice == "2":
        uninstall_hooks()
    else:
        print("Cancelled.")


if __name__ == "__main__":
    main()
