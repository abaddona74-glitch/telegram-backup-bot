import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    owner_id: int
    webhook_host: str
    webhook_port: int
    db_path: str

    @property
    def webhook_url(self) -> str:
        if self.webhook_host:
            return f"{self.webhook_host.rstrip('/')}/webhook"
        return ""


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set in .env file!")

    owner_id = os.getenv("OWNER_ID")
    if not owner_id:
        raise ValueError("OWNER_ID is not set in .env file!")

    return Config(
        bot_token=token,
        owner_id=int(owner_id),
        webhook_host=os.getenv("WEBHOOK_HOST", ""),
        webhook_port=int(os.getenv("WEBHOOK_PORT", "8080")),
        db_path=os.getenv("DB_PATH", "data/messages.db"),
    )
