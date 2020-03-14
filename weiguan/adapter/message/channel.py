import json
import asyncio

from aioredis import Redis, Channel


class MessageChannel:
    def __init__(self, config: dict, cache: Redis):
        self.config = config
        self.cache = cache
        self._handlers = []

        self.on_init = asyncio.create_task(self._init())

    async def _init(self):
        self.channel: Channel = (await self.cache.subscribe(
            '{}:{}:{}'.format(self.config['NAME'], 'message', 'channel')))[0]

        asyncio.create_task(self._handle())

    async def _handle(self):
        while (await self.channel.wait_message()):
            user_id, message = await self.channel.get_json()
            for handler in self._handlers:
                await handler(user_id, message)

    def add_handler(self, handler):
        self._handlers.append(handler)

    async def publish(self, user_id, message):
        await self.cache.publish_json(self.channel.name, (user_id, message))
