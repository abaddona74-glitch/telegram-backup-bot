from datetime import datetime, timezone


def format_user(row: dict) -> str:
    """Format contact display name from DB row."""
    name = row.get("from_user_name") or "Noma'lum"
    username = row.get("from_user_username")
    if username:
        return f"{name} (@{username})"
    return name


def format_datetime(ts: int) -> str:
    """Convert Unix timestamp to readable datetime string."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%d.%m.%Y %H:%M:%S UTC")


def format_deleted_message(row: dict) -> str:
    """Build notification text for a deleted message."""
    user = format_user(row)
    when = format_datetime(row["date"])
    content = row.get("text") or row.get("caption") or ""
    media = row.get("media_type")

    lines = [
        "🗑 <b>Xabar o'chirildi!</b>",
        "",
        f"👤 <b>Kim:</b> {user}",
        f"🕒 <b>Yuborilgan:</b> {when}",
    ]

    if media:
        media_icons = {
            "photo": "🖼",
            "video": "🎥",
            "voice": "🎤",
            "audio": "🎵",
            "document": "📄",
            "sticker": "🎭",
            "animation": "🎞",
            "video_note": "📹",
        }
        icon = media_icons.get(media, "📎")
        lines.append(f"{icon} <b>Media:</b> {media.capitalize()}")

    if content:
        # Truncate long messages
        if len(content) > 800:
            content = content[:800] + "…"
        lines.append(f"\n📝 <b>Matn:</b>\n{content}")
    elif not media:
        lines.append("\n📝 <b>Matn:</b> <i>(bo'sh yoki maxsus xabar)</i>")

    return "\n".join(lines)


def format_edited_message(old: dict, new_text: str, new_caption: str) -> str:
    """Build notification text for an edited message."""
    user = format_user(old)
    when_sent = format_datetime(old["date"])
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    when_edited = format_datetime(now_ts)

    old_content = old.get("text") or old.get("caption") or "<i>(matn yo'q)</i>"
    new_content = new_text or new_caption or "<i>(matn yo'q)</i>"

    if len(old_content) > 500:
        old_content = old_content[:500] + "…"
    if len(new_content) > 500:
        new_content = new_content[:500] + "…"

    lines = [
        "✏️ <b>Xabar tahrirlandi!</b>",
        "",
        f"👤 <b>Kim:</b> {user}",
        f"🕒 <b>Yuborilgan:</b> {when_sent}",
        f"🕒 <b>Tahrirlangan:</b> {when_edited}",
        "",
        f"❌ <b>Eski:</b>\n{old_content}",
        "",
        f"✅ <b>Yangi:</b>\n{new_content}",
    ]
    return "\n".join(lines)


def format_view_once_caption(row: dict) -> str:
    """Caption for saved view-once media."""
    user = format_user(row)
    when = format_datetime(row["date"])
    media = row.get("media_type", "media").capitalize()
    return (
        f"👁 <b>One-time {media} saqlandi!</b>\n\n"
        f"👤 <b>Kim:</b> {user}\n"
        f"🕒 <b>Yuborilgan:</b> {when}"
    )
