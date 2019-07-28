from enum import Enum
import traceback
from functools import wraps

from sanic import response
from sanic.exceptions import SanicException, Unauthorized

from ..models import UserSchema
from ..services import ServiceException, StorageService


class ResponseCode(Enum):
    OK = 0
    FAIL = 1


def response_json(code=ResponseCode.OK, message='', status=200, **data):
    return response.json({'code': code.value, 'message': message, 'data': data},
                         status)


def handle_exception(request, e):
    code = ResponseCode.FAIL
    message = repr(e)
    status = 500

    if isinstance(e, SanicException):
        status = e.status_code
    elif isinstance(e, ServiceException):
        message = e.message
        if e.code is not None:
            code = e.code
        status = 200

    data = {}
    if request.app.config['DEBUG']:
        data['exception'] = traceback.format_exc()

    return response_json(code, message, status, **data)


def authenticated():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request['session'].get('user') is None:
                raise Unauthorized('Not authenticated')

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator


async def dump_user_info(request, user):
    if user is None:
        return None

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    if user['avatar_id'] is not None:
        user['avatar'] = await storage_service.file_info(user['avatar_id'])

    return UserSchema().dump(user)


async def dump_user_infos(request, users):
    if not users:
        return []

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    avatar_users = [v for v in users if v['avatar_id'] is not None]
    files = await storage_service.file_infos(
        [v['avatar_id'] for v in avatar_users])
    for user, file in zip(avatar_users, files):
        user['avatar'] = file

    return [UserSchema().dump(v) for v in users]
