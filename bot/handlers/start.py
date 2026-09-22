"""
start.py — /start command and bot connection instructions.
"""
import logging
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.config import Config

logger = logging.getLogger(__name__)
router = Router()

CONNECT_INSTRUCTIONS = """
👋 <b>Salom! Telegram Backup Bot'ga xush kelibsiz!</b>

Bu bot sizning chatlaringizdagi:
🗑 <b>O'chirilgan xabarlar</b>ni saqlaydi
✏️ <b>Tahrirlangan xabarlar</b>ni kuzatadi
👁 <b>One-time / view-once media</b>ni saqlaydi

━━━━━━━━━━━━━━━━━━━━
🔌 <b>Botni ulash uchun:</b>

1. Telegram <b>Settings</b> → <b>Business</b> → <b>Chat Automation</b>
2. <b>"Bot"</b> maydoniga ushbu botni tanlang: @{username}
3. "Include all chats" yoki kerakli chatlarni tanlang
4. <b>Save</b> tugmasini bosing ✅

⚠️ <b>Eslatma:</b> Telegram Business yoki Premium kerak.
━━━━━━━━━━━━━━━━━━━━

Bot ulangandan so'ng barcha xabarlar avtomatik kuzatiladi!
"""


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, config: Config) -> None:
    """Send connection instructions when user types /start."""
    # Only the owner should use this
    if message.from_user and message.from_user.id != config.owner_id:
        await message.answer(
            "⛔️ Bu bot shaxsiy foydalanish uchun mo'ljallangan.",
            parse_mode="HTML",
        )
        return

    me = await bot.get_me()
    username = me.username or "your_bot"

    await message.answer(
        CONNECT_INSTRUCTIONS.format(username=username),
        parse_mode="HTML",
    )
