import json
from typing import Optional, Tuple
from aiogram.types import Message


def extract_message_data(
    msg: Message,
    business_connection_id: str,
) -> dict:
    """
    Extract all relevant fields from an aiogram Message object
    and return a dict suitable for DB insertion.
    """
    user = msg.from_user
    from_user_id = user.id if user else None
    from_user_name = None
    from_user_username = None

    if user:
        parts = [user.first_name or "", user.last_name or ""]
        from_user_name = " ".join(p for p in parts if p).strip() or None
        from_user_username = user.username

    # Detect media type and file_id
    media_type, file_id, file_unique_id, is_view_once = _detect_media(msg)

    # Minimal raw JSON snapshot (avoid storing huge objects)
    try:
        raw = json.dumps(msg.model_dump(exclude_none=True), default=str)[:4096]
    except Exception:
        raw = "{}"

    return {
        "message_id": msg.message_id,
        "business_connection_id": business_connection_id,
        "chat_id": msg.chat.id,
        "from_user_id": from_user_id,
        "from_user_name": from_user_name,
        "from_user_username": from_user_username,
        "text": msg.text,
        "caption": msg.caption,
        "media_type": media_type,
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "date": int(msg.date.timestamp()),
        "is_view_once": 1 if is_view_once else 0,
        "raw_json": raw,
    }


def _detect_media(msg: Message) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """Return (media_type, file_id, file_unique_id, is_view_once)."""

    # View-once photo
    if msg.photo and getattr(msg, "has_protected_content", False):
        largest = max(msg.photo, key=lambda p: p.file_size or 0)
        return "photo", largest.file_id, largest.file_unique_id, True

    # View-once video (video_once flag in newer Telegram versions)
    if msg.video and getattr(msg, "has_protected_content", False):
        return "video", msg.video.file_id, msg.video.file_unique_id, True

    # Regular photo
    if msg.photo:
        largest = max(msg.photo, key=lambda p: p.file_size or 0)
        return "photo", largest.file_id, largest.file_unique_id, False

    # Regular video
    if msg.video:
        return "video", msg.video.file_id, msg.video.file_unique_id, False

    # Voice
    if msg.voice:
        return "voice", msg.voice.file_id, msg.voice.file_unique_id, False

    # Audio
    if msg.audio:
        return "audio", msg.audio.file_id, msg.audio.file_unique_id, False

    # Document
    if msg.document:
        return "document", msg.document.file_id, msg.document.file_unique_id, False

    # Sticker
    if msg.sticker:
        return "sticker", msg.sticker.file_id, msg.sticker.file_unique_id, False

    # Animation (GIF)
    if msg.animation:
        return "animation", msg.animation.file_id, msg.animation.file_unique_id, False

    # Video note (round video)
    if msg.video_note:
        return "video_note", msg.video_note.file_id, msg.video_note.file_unique_id, False

    return None, None, None, False
