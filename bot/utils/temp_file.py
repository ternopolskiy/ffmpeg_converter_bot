import os
import uuid

from bot.config import settings


def temp_path(extension: str) -> str:
    name = f"{uuid.uuid4().hex}.{extension.lstrip('.')}"
    return os.path.join(settings.temp_dir, name)


def cleanup(*paths: str) -> None:
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass
