import asyncio
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from bot.config import settings

# MAXIMUM 3 CONVERSION
_conversion_semaphore = asyncio.Semaphore(3)


@dataclass
class ConversionResult:
    success: bool
    input_path: str
    output_path: str
    original_size_mb: float
    converted_size_mb: float
    duration: float
    error: str | None = None


async def convert_flac_to_mp3(input_path: str) -> ConversionResult:
    async with _conversion_semaphore:
        start = time.monotonic()

        stem = Path(input_path).stem
        output_path = os.path.join(
            settings.temp_dir, f"{stem}_{uuid.uuid4().hex[:8]}.mp3"
        )

        original_size = os.path.getsize(input_path) / (1024 * 1024)

        cmd = [
            settings.ffmpeg_path,
            "-y",
            "-i", input_path,
            "-vn",
            "-codec:a", "libmp3lame",
            "-b:a", "320k",
            "-map_metadata", "0",
            "-id3v2_version", "3",
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        duration = time.monotonic() - start

        if proc.returncode != 0:
            return ConversionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                original_size_mb=original_size,
                converted_size_mb=0,
                duration=duration,
                error=stderr.decode("utf-8", errors="replace")[-500:],
            )

        converted_size = os.path.getsize(output_path) / (1024 * 1024)

        return ConversionResult(
            success=True,
            input_path=input_path,
            output_path=output_path,
            original_size_mb=original_size,
            converted_size_mb=converted_size,
            duration=duration,
        )
