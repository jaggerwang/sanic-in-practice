import asyncio

from ..utils import Singleton
from ..models import NormalMessage, NormalMessageSchema, NotifyMessage, \
    NotifyMessageSchema


class MessageService(metaclass=Singleton):
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

        self.wss = {}

    async def init(self):
        self.channel = (await self.cache.subscribe(self.chan))[0]

        asyncio.create_task(self.handle_channel_message())

    @property
    def chan(self):
        return '{}:{}:{}'.format(self.config['NAME'], 'message', 'channel')

    async def handle_channel_message(self):
        while await self.channel.wait_message():
            user_id, message = await self.channel.get_json()
            if user_id is None:
                for ws in self.wss.values():
                    await ws.send(message)
            else:
                ws = self.wss.get(user_id)
                if ws is not None:
                    await ws.send(message)

    def register_ws(self, user_id, ws):
        self.wss[user_id] = ws

    def unregister_ws(self, user_id):
        del self.wss[user_id]

    def dump_message(self, message):
        if isinstance(message, NormalMessage):
            message = NormalMessageSchema().dumps(message)
        elif isinstance(message, NotifyMessage):
            message = NotifyMessageSchema().dumps(message)

        return message

    async def send_user_message(self, user_id, message):
        await self.cache.publish_json(
            self.chan, (user_id, self.dump_message(message)))

    async def broadcast_message(self, message):
        await self.cache.publish_json(
            self.chan, (None, self.dump_message(message)))
