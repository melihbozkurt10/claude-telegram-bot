"""Configuration management for Claude Code Telegram Bot"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Bot configuration from environment variables"""

    # Telegram settings
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Notification settings
    NOTIFY_ON_ERROR: bool = os.getenv("NOTIFY_ON_ERROR", "true").lower() == "true"
    NOTIFY_ON_COMPLETE: bool = os.getenv("NOTIFY_ON_COMPLETE", "true").lower() == "true"
    NOTIFY_ON_LONG_RUNNING: bool = os.getenv("NOTIFY_ON_LONG_RUNNING", "true").lower() == "true"
    LONG_RUNNING_THRESHOLD: int = int(os.getenv("LONG_RUNNING_THRESHOLD", "30"))

    # Paths
    PROJECT_DIR: Path = Path(__file__).parent.parent
    STATE_DIR: Path = PROJECT_DIR / "state"
    STATE_FILE: Path = STATE_DIR / "session.json"

    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            return False, "TELEGRAM_BOT_TOKEN is not set"
        if not cls.CHAT_ID:
            return False, "TELEGRAM_CHAT_ID is not set"
        return True, "Configuration is valid"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Ensure required directories exist"""
        cls.STATE_DIR.mkdir(parents=True, exist_ok=True)
