from sanic import Blueprint, response

from .schema import NormalMessageSchema, NotifyMessageSchema
from ...container import Container
from ...entity import MessageLevel, NormalMessage, NotifyMessage
from .common import response_json

message_blueprint = Blueprint('message', url_prefix='/message')


@message_blueprint.websocket('/ws')
async def ws(request, ws):
    user = request['session'].get('user')
    if user is None:
        await ws.send(NormalMessageSchema().dumps(
            NormalMessage('未登录', level=MessageLevel.ERROR.value)))
        return

    message_broker = Container().message_broker
    message_broker.register_ws(user['id'], ws)

    await message_broker.broadcast_message(
        _dump_message(NormalMessage(
            'Welcome user {}!'.format(user['username']))))

    try:
        async for message in ws:
            await message_broker.send_user_message(
                user['id'],
                _dump_message(NormalMessage(
                    'Message received: {}'.format(message))))
    finally:
        message_broker.unregister_ws(user['id'])


def _dump_message(self, message):
    if isinstance(message, NormalMessage):
        message = NormalMessageSchema().dumps(message)
    elif isinstance(message, NotifyMessage):
        message = NotifyMessageSchema().dumps(message)

    return message
