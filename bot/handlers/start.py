"""
start.py — /start command and bot connection instructions.
"""
import logging
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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

1. Quyidagi <b>"🔌 Connect"</b> tugmasini bosing
2. <b>Telegram Business</b> → <b>Chat Automation</b> (yoki <b>Bots</b>) bo'limiga o'ting
3. <b>"Bot"</b> maydoniga ushbu botni tanlang: @{username}
4. <b>Save</b> tugmasini bosing ✅

⚠️ <i>Eslatma: Bu funksiya Telegram Premium/Business akkauntlarda ishlaydi.</i>
━━━━━━━━━━━━━━━━━━━━
"""


def get_start_keyboard(username: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with Connect button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔌 Connect",
                    url="tg://settings/edit",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Qanday ishlaydi?",
                    callback_data="how_it_works",
                )
            ],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, config: Config) -> None:
    """Send connection instructions when user types /start."""
    # Only owners configured in OWNER_IDS should use this
    if message.from_user and message.from_user.id not in config.owner_ids:
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
        reply_markup=get_start_keyboard(username),
    )


@router.callback_query(F.data == "how_it_works")
async def cb_how_it_works(callback: CallbackQuery, bot: Bot) -> None:
    """Explain how the bot works upon callback query."""
    me = await bot.get_me()
    username = me.username or "your_bot"

    text = (
        "📖 <b>Bot qanday ishlaydi?</b>\n\n"
        "1. Siz botni Telegram Business orqali akkauntingizga ulaysiz.\n"
        "2. Suhbatdoshlaringiz sizga yuborgan va keyin o'chirib yuborgan xabarlari bazada saqlanadi.\n"
        "3. Xabar o'chirilishi bilan bot sizga xabarning asl matni yoki rasmini yuboradi.\n"
        "4. Tahrirlangan xabarlarda ham eski va yangi variantlar ko'rsatiladi.\n\n"
        f"Ulash uchun: <code>@{username}</code>"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
