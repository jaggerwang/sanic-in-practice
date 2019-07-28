from sanic import Blueprint, response
from sanic.exceptions import NotFound

from ..models import WsMessageLevel, WsMessage, WsMessageSchema
from .common import ResponseCode, response_json

message = Blueprint('message', url_prefix='/message')


@message.websocket('/ws')
async def ws(request, ws):
    user = request['session'].get('user')
    if user is None:
        await ws.send(WsMessageSchema().dumps(
            WsMessage('未登录', level=WsMessageLevel.ERROR.value)))
        return

    request.app.ws.register_ws_user(user['id'], ws)

    await request.app.ws.broadcast_message(
        WsMessage('Welcome user {}'.format(user['username'])))

    try:
        async for message in ws:
            await request.app.ws.send_user_message(
                user['id'], WsMessage('Message received: {}'.format(message)))
    finally:
        request.app.ws.unregister_ws_user(user['id'])
