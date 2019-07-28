from enum import Enum
import uuid
import asyncio

from marshmallow import Schema, fields

from ..utils import local_now


class WsManager(object):
    ws_users = {}

    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    @property
    def channel_name(self):
        return '{}:{}:{}'.format(self.config['NAME'], 'message', 'ws')

    async def init(self):
        self.channel = (await self.cache.subscribe(self.channel_name))[0]

        asyncio.create_task(self.handle_channel_message())

    async def handle_channel_message(self):
        while await self.channel.wait_message():
            user_id, message = await self.channel.get_json()
            if user_id is None:
                for ws in self.ws_users.values():
                    await ws.send(message)
            else:
                ws = self.ws_users.get(user_id)
                if ws is not None:
                    await ws.send(message)

    def register_ws_user(self, user_id, ws):
        self.ws_users[user_id] = ws

    def unregister_ws_user(self, user_id):
        del self.ws_users[user_id]

    async def send_user_message(self, user_id, message):
        await self.cache.publish_json(
            self.channel_name, (user_id, WsMessageSchema().dumps(message)))

    async def broadcast_message(self, message):
        await self.cache.publish_json(
            self.channel_name, (None, WsMessageSchema().dumps(message)))


class WsMessageType(Enum):
    MESSAGE = 'message'
    NOTIFY = 'notify'


class WsMessageLevel(Enum):
    INFO = 'info'
    ERROR = 'error'


class WsMessage(object):
    def __init__(self, content, title='', type=WsMessageType.MESSAGE.value,
                 level=WsMessageLevel.INFO.value):
        self.id = uuid.uuid4()
        self.type = type
        self.title = title
        self.content = content
        self.level = level
        self.created_at = local_now()


class WsMessageSchema(Schema):
    id = fields.UUID()
    type = fields.String()
    title = fields.String()
    content = fields.String()
    level = fields.String()
    createdAt = fields.DateTime(attribute='created_at')
