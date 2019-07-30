from sanic import Blueprint, response
from sanic.exceptions import NotFound

from ..models import MessageLevel, NormalMessage, NormalMessageSchema
from ..services import MessageService
from .common import ResponseCode, response_json

message = Blueprint('message', url_prefix='/message')


@message.websocket('/ws')
async def ws(request, ws):
    user = request['session'].get('user')
    if user is None:
        await ws.send(NormalMessageSchema().dumps(
            NormalMessage('未登录', level=MessageLevel.ERROR.value)))
        return

    request.app.message_service.register_ws(user['id'], ws)

    await request.app.message_service.broadcast_message(
        NormalMessage('Welcome user {}!'.format(user['username'])))

    try:
        async for message in ws:
            await request.app.message_service.send_user_message(
                user['id'],
                NormalMessage('Message received: {}'.format(message)))
    finally:
        request.app.message_service.unregister_ws(user['id'])
