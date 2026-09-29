"""
edited.py — Handler for edited business messages.

When a message is edited, compare with the stored version and notify owner.
"""
import logging
from aiogram import Router, Bot
from aiogram.types import Message

from bot.config import Config
from bot.database import get_message, save_message, get_connection_owner
from bot.utils.media_saver import extract_message_data
from bot.utils.formatters import format_edited_message

logger = logging.getLogger(__name__)
router = Router()


@router.edited_business_message()
async def handle_edited_message(message: Message, bot: Bot, config: Config) -> None:
    """Detect edits in business messages and notify owner with diff."""
    bc_id = message.business_connection_id
    if not bc_id:
        return

    # Fetch the original from DB
    old = await get_message(config.db_path, message.message_id, bc_id, message.chat.id)

    new_text = message.text or ""
    new_caption = message.caption or ""

    if old is None:
        # Not saved before — just save the new version silently
        data = extract_message_data(message, bc_id)
        await save_message(config.db_path, data)
        logger.warning("Edited message %s not found in DB — saved new version", message.message_id)
        return

    old_text = old.get("text") or ""
    old_caption = old.get("caption") or ""

    # Only notify if text actually changed
    if new_text == old_text and new_caption == old_caption:
        logger.debug("Message %s re-edited with same content, skipping", message.message_id)
        return

    target_id = await get_connection_owner(config.db_path, bc_id, bot)
    if not target_id:
        if len(config.owner_ids) == 1:
            target_id = config.owner_id
        else:
            logger.warning(
                "Could not determine owner for business connection %s, skipping edit notification",
                bc_id,
            )
            return

    # If the message was sent by the owner, update DB silently and skip notification
    from_user_id = message.from_user.id if message.from_user else old.get("from_user_id")
    if from_user_id and (from_user_id == target_id or from_user_id in config.owner_ids):
        logger.debug("Message %s edited by owner (%s), updating DB silently", message.message_id, from_user_id)
        new_data = extract_message_data(message, bc_id)
        await save_message(config.db_path, new_data)
        return

    text = format_edited_message(old, new_text, new_caption)

    try:
        await bot.send_message(
            chat_id=target_id,
            text=text,
            parse_mode="HTML",
        )
        logger.info("Notified owner %s about edited message %s", target_id, message.message_id)
    except Exception as e:
        logger.error("Failed to notify owner %s about edit: %s", target_id, e)

    # Update DB with the new version
    new_data = extract_message_data(message, bc_id)
    await save_message(config.db_path, new_data)
