from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis

from bot.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.rate = settings.throttle_rate

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        key = f"throttle:{user_id}"

        if await self.redis.exists(key):
            ttl = await self.redis.ttl(key)
            await event.answer(
                f"⏳ Подожди ещё {ttl} сек. перед следующей отправкой."
            )
            return

        await self.redis.setex(key, int(self.rate), "1")
        return await handler(event, data)
