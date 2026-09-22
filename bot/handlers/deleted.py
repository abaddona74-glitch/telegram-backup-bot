"""
deleted.py — Handler for deleted business messages.

When a message is deleted, fetch it from DB and notify the owner.
"""
import logging
from aiogram import Router, Bot
from aiogram.types import BusinessMessagesDeleted

from bot.config import Config
from bot.database import get_message, delete_message
from bot.utils.formatters import format_deleted_message

logger = logging.getLogger(__name__)
router = Router()


@router.deleted_business_messages()
async def handle_deleted_messages(
    event: BusinessMessagesDeleted,
    bot: Bot,
    config: Config,
) -> None:
    """Notify owner about each deleted business message."""
    bc_id = event.business_connection_id
    chat_id = event.chat.id

    for msg_id in event.message_ids:
        row = await get_message(config.db_path, msg_id, bc_id, chat_id)

        if row is None:
            logger.warning("Deleted message %s not found in DB", msg_id)
            # Still notify — message not in our DB
            await bot.send_message(
                chat_id=config.owner_id,
                text=(
                    "🗑 <b>Xabar o'chirildi!</b>\n\n"
                    f"📌 <b>Chat ID:</b> <code>{chat_id}</code>\n"
                    f"📌 <b>Xabar ID:</b> <code>{msg_id}</code>\n\n"
                    "<i>(Mazmuni saqlanmagan — bot ishga tushishidan oldin yoki restart bo'lgandan keyin yuborilgan)</i>"
                ),
                parse_mode="HTML",
            )
            continue

        # Format and send notification
        text = format_deleted_message(row)
        try:
            await bot.send_message(
                chat_id=config.owner_id,
                text=text,
                parse_mode="HTML",
            )

            # If the deleted message had media — resend it
            if row.get("file_id") and row.get("media_type"):
                await _resend_media(bot, config.owner_id, row)

            logger.info("Notified owner about deleted message %s", msg_id)
        except Exception as e:
            logger.error("Failed to notify owner about deleted msg %s: %s", msg_id, e)
        finally:
            # Clean up DB entry
            await delete_message(config.db_path, msg_id, bc_id, chat_id)


async def _resend_media(bot: Bot, owner_id: int, row: dict) -> None:
    """Re-send the media from a deleted message to the owner."""
    media_type = row["media_type"]
    file_id = row["file_id"]
    caption = "☝️ <i>O'chirilgan xabardagi media:</i>"

    try:
        if media_type == "photo":
            await bot.send_photo(owner_id, photo=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "video":
            await bot.send_video(owner_id, video=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "voice":
            await bot.send_voice(owner_id, voice=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "audio":
            await bot.send_audio(owner_id, audio=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "document":
            await bot.send_document(owner_id, document=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "sticker":
            await bot.send_sticker(owner_id, sticker=file_id)
        elif media_type == "animation":
            await bot.send_animation(owner_id, animation=file_id, caption=caption, parse_mode="HTML")
        elif media_type == "video_note":
            await bot.send_video_note(owner_id, video_note=file_id)
    except Exception as e:
        logger.error("Failed to resend media for deleted msg: %s", e)
