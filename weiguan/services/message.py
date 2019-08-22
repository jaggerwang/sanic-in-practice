from ..entities import NormalMessage, NormalMessageSchema, NotifyMessage, \
    NotifyMessageSchema
from ..dependencies import MessageChannel


class MessageService():
    _wss = {}

    def __init__(self, config: dict, channel: MessageChannel):
        self.config = config
        self.channel = channel

        self.channel.add_handler(self._handle_message)

    async def _handle_message(self, user_id, message):
        if user_id is None:
            for ws in self._wss.values():
                await ws.send(message)
        else:
            ws = self._wss.get(user_id)
            if ws is not None:
                await ws.send(message)

    def register_ws(self, user_id, ws):
        self._wss[user_id] = ws

    def unregister_ws(self, user_id):
        del self._wss[user_id]

    async def send_user_message(self, user_id, message):
        await self.channel.publish(user_id, self._dump_message(message))

    async def broadcast_message(self, message):
        await self.channel.publish(None, self._dump_message(message))

    def _dump_message(self, message):
        if isinstance(message, NormalMessage):
            message = NormalMessageSchema().dumps(message)
        elif isinstance(message, NotifyMessage):
            message = NotifyMessageSchema().dumps(message)

        return message
