"""
business.py — Incoming business messages handler.

Saves every message sent through Chat Automation to the DB.
Also triggers view-once media forwarding to the owner.
"""
import logging
from aiogram import Router, Bot
from aiogram.types import Message

from bot.config import Config
from bot.database import save_message, get_connection_owner
from bot.utils.media_saver import extract_message_data
from bot.utils.formatters import format_view_once_caption

logger = logging.getLogger(__name__)
router = Router()


@router.business_message()
async def handle_business_message(message: Message, bot: Bot, config: Config) -> None:
    """Handle all incoming business messages — save to DB and check for view-once."""
    bc_id = message.business_connection_id
    if not bc_id:
        return  # Not a business message

    data = extract_message_data(message, bc_id)
    await save_message(config.db_path, data)

    logger.info(
        "Saved business message %s from chat %s (view_once=%s)",
        message.message_id,
        message.chat.id,
        bool(data["is_view_once"]),
    )

    # If view-once media — immediately forward to connection owner
    if data["is_view_once"] and data["file_id"]:
        target_id = await get_connection_owner(config.db_path, bc_id) or config.owner_id
        await _forward_view_once(bot, target_id, data)


async def _forward_view_once(bot: Bot, target_id: int, data: dict) -> None:
    """Send the view-once media to the owner of this business account."""
    caption = format_view_once_caption(data)
    media_type = data["media_type"]
    file_id = data["file_id"]

    try:
        if media_type == "photo":
            await bot.send_photo(
                chat_id=target_id,
                photo=file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif media_type == "video":
            await bot.send_video(
                chat_id=target_id,
                video=file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif media_type == "voice":
            await bot.send_voice(
                chat_id=target_id,
                voice=file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif media_type == "video_note":
            await bot.send_message(
                chat_id=target_id,
                text=caption,
                parse_mode="HTML",
            )
            await bot.send_video_note(
                chat_id=target_id,
                video_note=file_id,
            )
        else:
            await bot.send_message(
                chat_id=target_id,
                text=caption,
                parse_mode="HTML",
            )
        logger.info("Forwarded view-once %s to owner %s", media_type, target_id)
    except Exception as e:
        logger.error("Failed to forward view-once media: %s", e)
