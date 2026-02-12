from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    tg = message.from_user

    result = await session.execute(
        select(User).where(User.telegram_id == tg.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=tg.id,
            username=tg.username,
            first_name=tg.first_name,
        )
        session.add(user)

    await message.answer(
        "🎵 <b>FLAC → MP3 конвертер</b>\n\n"
        "Отправь мне один или несколько <b>.flac</b> файлов, "
        "и я верну MP3 320 kbps.\n\n"
        "📌 Лимит Telegram: файл до 50 МБ.\n"
        "📌 Можно кидать сразу пачкой.\n\n"
        "/stats — твоя статистика",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    count = user.total_conversions if user else 0
    await message.answer(f"📊 Всего конвертаций: <b>{count}</b>", parse_mode="HTML")
