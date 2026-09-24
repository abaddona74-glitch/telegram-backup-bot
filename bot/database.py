import logging
import os
import aiosqlite
from typing import Optional
from aiogram import Bot

logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


async def init_db(db_path: str) -> None:
    """Create tables if they don't exist."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                business_connection_id TEXT NOT NULL,
                chat_id INTEGER NOT NULL,
                from_user_id INTEGER,
                from_user_name TEXT,
                from_user_username TEXT,
                text TEXT,
                caption TEXT,
                media_type TEXT,
                file_id TEXT,
                file_unique_id TEXT,
                date INTEGER NOT NULL,
                is_view_once INTEGER DEFAULT 0,
                raw_json TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        await db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_msg_unique
            ON messages(message_id, business_connection_id, chat_id)
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS business_connections (
                connection_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        await db.commit()


async def save_message(db_path: str, msg_data: dict) -> None:
    """Save or update a message in the database."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO messages (
                message_id, business_connection_id, chat_id,
                from_user_id, from_user_name, from_user_username,
                text, caption, media_type, file_id, file_unique_id,
                date, is_view_once, raw_json
            ) VALUES (
                :message_id, :business_connection_id, :chat_id,
                :from_user_id, :from_user_name, :from_user_username,
                :text, :caption, :media_type, :file_id, :file_unique_id,
                :date, :is_view_once, :raw_json
            )
            ON CONFLICT(message_id, business_connection_id, chat_id) DO UPDATE SET
                text = excluded.text,
                caption = excluded.caption,
                file_id = excluded.file_id,
                raw_json = excluded.raw_json
        """, msg_data)
        await db.commit()


async def get_message(
    db_path: str,
    message_id: int,
    business_connection_id: str,
    chat_id: int,
) -> Optional[dict]:
    """Retrieve a stored message by its IDs."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM messages
            WHERE message_id = ? AND business_connection_id = ? AND chat_id = ?
        """, (message_id, business_connection_id, chat_id)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def delete_message(
    db_path: str,
    message_id: int,
    business_connection_id: str,
    chat_id: int,
) -> None:
    """Remove a message from the database after notifying owner."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            DELETE FROM messages
            WHERE message_id = ? AND business_connection_id = ? AND chat_id = ?
        """, (message_id, business_connection_id, chat_id))
        await db.commit()


async def save_business_connection(
    db_path: str,
    connection_id: str,
    user_id: int,
    is_enabled: int = 1,
) -> None:
    """Save or update business connection owner mapping."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO business_connections (connection_id, user_id, is_enabled, updated_at)
            VALUES (?, ?, ?, strftime('%s', 'now'))
            ON CONFLICT(connection_id) DO UPDATE SET
                user_id = excluded.user_id,
                is_enabled = excluded.is_enabled,
                updated_at = excluded.updated_at
        """, (connection_id, user_id, is_enabled))
        await db.commit()


async def get_connection_owner(
    db_path: str,
    connection_id: str,
    bot: Optional[Bot] = None,
) -> Optional[int]:
    """Get the user_id that owns the specified business connection."""
    if not connection_id:
        return None
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("""
            SELECT user_id FROM business_connections
            WHERE connection_id = ?
        """, (connection_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return int(row[0])

    # If missing from DB (e.g. after container restart), query Telegram API directly
    if bot:
        try:
            conn = await bot.get_business_connection(connection_id)
            if conn and conn.user:
                user_id = conn.user.id
                await save_business_connection(
                    db_path,
                    connection_id=connection_id,
                    user_id=user_id,
                    is_enabled=1 if conn.is_enabled else 0,
                )
                logger.info("Restored business connection %s owner %s from Telegram API", connection_id, user_id)
                return user_id
        except Exception as e:
            logger.warning("Could not fetch business connection %s from Telegram: %s", connection_id, e)

    return None
