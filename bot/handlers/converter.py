import os

from aiogram import Bot, F, Router
from aiogram.types import FSInputFile, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.models import ConversionLog, User
from bot.services.audio_converter import convert_flac_to_mp3
from bot.utils.temp_file import cleanup, temp_path

router = Router()


def _is_flac_document(message: Message) -> bool:
    """Файл отправлен как документ и это .flac"""
    doc = message.document
    if not doc:
        return False
    name = (doc.file_name or "").lower()
    mime = (doc.mime_type or "").lower()
    return name.endswith(".flac") or mime in ("audio/flac", "audio/x-flac")


def _is_flac_audio(message: Message) -> bool:
    """Файл отправлен как аудио и это .flac"""
    audio = message.audio
    if not audio:
        return False
    name = (audio.file_name or "").lower()
    mime = (audio.mime_type or "").lower()
    return name.endswith(".flac") or mime in ("audio/flac", "audio/x-flac")


async def _process_flac(
    message: Message,
    bot: Bot,
    session: AsyncSession,
    file_id: str,
    file_name: str,
    file_size: int,
):
    size_mb = file_size / (1024 * 1024)

    # Telegram Bot API лимит на скачивание — 20 МБ
    if size_mb > 20:
        await message.answer(
            f"❌ Файл <b>{file_name}</b> весит {size_mb:.1f} МБ.\n\n"
            f"⚠️ Telegram Bot API может скачивать файлы только до <b>20 МБ</b>.\n\n"
            f"Для работы с большими файлами нужно поднять свой "
            f"<a href='https://github.com/tdlib/telegram-bot-api'>Telegram Bot API Server</a> "
            f"(лимит до 2000 МБ).",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return

    if size_mb > settings.max_file_size_mb:
        await message.answer(
            f"❌ Файл <b>{file_name}</b> весит {size_mb:.1f} МБ — "
            f"лимит {settings.max_file_size_mb} МБ.",
            parse_mode="HTML",
        )
        return

    status = await message.answer(
        f"⏬ Скачиваю <b>{file_name}</b> ({size_mb:.1f} МБ)…",
        parse_mode="HTML",
    )

    input_path = temp_path("flac")
    try:
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, destination=input_path)
    except Exception as e:
        cleanup(input_path)
        error_msg = str(e)
        if "too big" in error_msg.lower():
            await status.edit_text(
                f"❌ Файл слишком большой для Telegram Bot API (лимит 20 МБ).\n\n"
                f"Для больших файлов нужен свой Bot API Server.",
                parse_mode="HTML",
            )
        else:
            await status.edit_text(f"❌ Не удалось скачать: {e}")
        return

    await status.edit_text(
        f"🔄 Конвертирую <b>{file_name}</b> → MP3 320 kbps…",
        parse_mode="HTML",
    )

    result = await convert_flac_to_mp3(input_path)

    if not result.success:
        cleanup(input_path, result.output_path)
        await status.edit_text(
            f"❌ Ошибка конвертации:\n<code>{result.error}</code>",
            parse_mode="HTML",
        )
        return

    mp3_name = os.path.splitext(file_name)[0] + ".mp3"

    await status.edit_text(
        f"⬆️ Отправляю <b>{mp3_name}</b> ({result.converted_size_mb:.1f} МБ)…",
        parse_mode="HTML",
    )

    try:
        await message.answer_document(
            document=FSInputFile(result.output_path, filename=mp3_name),
            caption=(
                f"✅ <b>{mp3_name}</b>\n"
                f"📦 {result.original_size_mb:.1f} МБ → "
                f"{result.converted_size_mb:.1f} МБ\n"
                f"⏱ {result.duration:.1f} сек."
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        await status.edit_text(f"❌ Не удалось отправить: {e}")
    finally:
        cleanup(input_path, result.output_path)

    log = ConversionLog(
        telegram_id=message.from_user.id,
        original_filename=file_name,
        original_size_mb=result.original_size_mb,
        converted_size_mb=result.converted_size_mb,
        duration_seconds=result.duration,
    )
    session.add(log)

    user_result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.total_conversions += 1

    await status.delete()


@router.message(F.document, _is_flac_document)
async def handle_flac_document(message: Message, bot: Bot, session: AsyncSession):
    doc = message.document
    await _process_flac(
        message=message,
        bot=bot,
        session=session,
        file_id=doc.file_id,
        file_name=doc.file_name or "audio.flac",
        file_size=doc.file_size or 0,
    )


@router.message(F.audio, _is_flac_audio)
async def handle_flac_audio(message: Message, bot: Bot, session: AsyncSession):
    audio = message.audio
    await _process_flac(
        message=message,
        bot=bot,
        session=session,
        file_id=audio.file_id,
        file_name=audio.file_name or "audio.flac",
        file_size=audio.file_size or 0,
    )


@router.message(F.audio)
async def handle_non_flac_audio(message: Message):
    mime = message.audio.mime_type or "unknown"
    name = message.audio.file_name or "unknown"
    await message.answer(
        f"⚠️ Это <b>{mime}</b> ({name}).\n"
        f"Я конвертирую только <b>.flac</b> файлы.",
        parse_mode="HTML",
    )


@router.message(F.document)
async def handle_wrong_format(message: Message):
    await message.answer(
        "⚠️ Я принимаю только <b>.flac</b> файлы.",
        parse_mode="HTML",
    )
