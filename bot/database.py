import os
import aiosqlite
from typing import Optional

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
