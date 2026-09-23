import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    owner_ids: list[int]
    webhook_host: str
    webhook_port: int
    db_path: str

    @property
    def owner_id(self) -> int:
        """First owner ID for backward compatibility."""
        return self.owner_ids[0] if self.owner_ids else 0

    @property
    def webhook_url(self) -> str:
        if self.webhook_host:
            return f"{self.webhook_host.rstrip('/')}/webhook"
        return ""


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set in .env file!")

    raw_owners = os.getenv("OWNER_IDS") or os.getenv("OWNER_ID")
    if not raw_owners:
        raise ValueError("Neither OWNER_IDS nor OWNER_ID is set in .env file!")

    owner_ids = [
        int(item.strip())
        for item in raw_owners.replace(";", ",").split(",")
        if item.strip().lstrip("-").isdigit()
    ]
    if not owner_ids:
        raise ValueError("No valid Telegram IDs found in OWNER_IDS / OWNER_ID!")

    return Config(
        bot_token=token,
        owner_ids=owner_ids,
        webhook_host=os.getenv("WEBHOOK_HOST") or os.getenv("RENDER_EXTERNAL_URL", ""),
        webhook_port=int(os.getenv("PORT") or os.getenv("WEBHOOK_PORT", "8080")),
        db_path=os.getenv("DB_PATH", "data/messages.db"),
    )
