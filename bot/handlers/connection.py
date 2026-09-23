"""
connection.py — Handler for Telegram Business connection updates.

Tracks which Telegram user created which business connection.
Ensures notifications are sent to the correct owner account.
"""
import logging
from aiogram import Router, Bot
from aiogram.types import BusinessConnection

from bot.config import Config
from bot.database import save_business_connection

logger = logging.getLogger(__name__)
router = Router()


@router.business_connection()
async def handle_business_connection(
    connection: BusinessConnection,
    bot: Bot,
    config: Config,
) -> None:
    """Handle new business connection or disconnection."""
    user_id = connection.user.id
    conn_id = connection.id
    is_enabled = connection.is_enabled
    chat_id = connection.user_chat_id

    # Security check: only users configured in OWNER_IDS can connect
    if user_id not in config.owner_ids:
        logger.warning(
            "Unauthorized user %s (%s) tried to connect business connection %s",
            user_id,
            connection.user.full_name,
            conn_id,
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="⛔️ <b>Ruxsat berilmadi!</b>\n\nSiz bot sozlamalaridagi OWNER_IDS ro'yxatida emassiz.",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error("Failed to notify unauthorized user: %s", e)
        return

    # Save connection to DB
    await save_business_connection(
        config.db_path,
        connection_id=conn_id,
        user_id=user_id,
        is_enabled=1 if is_enabled else 0,
    )

    if is_enabled:
        logger.info(
            "Business connection %s activated for user %s (%s)",
            conn_id,
            user_id,
            connection.user.full_name,
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "✅ <b>Bot hisobingizga muvaffaqiyatli ulandi!</b>\n\n"
                    "Endi ushbu akkauntdagi:\n"
                    "🗑 <i>O'chirilgan xabarlar</i>\n"
                    "✏️ <i>Tahrirlangan xabarlar</i>\n"
                    "👁 <i>View-once media fayllari</i>\n\n"
                    "to'g'ridan-to'g'ri sizga yuboriladi."
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error("Failed to send connection confirmation to %s: %s", user_id, e)
    else:
        logger.info(
            "Business connection %s deactivated for user %s",
            conn_id,
            user_id,
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="⚠️ <b>Bot Telegram Business hisobingizdan uzildi.</b>",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error("Failed to send disconnect notification to %s: %s", user_id, e)
