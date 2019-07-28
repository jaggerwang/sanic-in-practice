from enum import Enum
import traceback
from functools import wraps

from sanic import response
from sanic.exceptions import SanicException, Unauthorized
from pymysql.err import IntegrityError

from ..models import PostSchema, UserSchema
from ..services import ServiceException, StorageService, UserService, \
    StatService


class ResponseCode(Enum):
    OK = 'ok'
    FAIL = 'fail'
    DUPLICATE = 'duplicate'


def response_json(code=ResponseCode.OK, message='', status=200, **data):
    return response.json({'code': code.value, 'message': message, 'data': data},
                         status)


def handle_exception(request, e):
    code = ResponseCode.FAIL
    message = repr(e)
    status = 500

    if isinstance(e, SanicException):
        status = e.status_code
    elif isinstance(e, IntegrityError):
        code = ResponseCode.DUPLICATE
        status = 200
    elif isinstance(e, ServiceException):
        message = e.message
        if e.code is not None:
            code = e.code
        status = 200

    data = {}
    if request.app.config['DEBUG']:
        traceback.print_exc()
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
    user['avatar'] = await storage_service.file_info(user['avatar_id'])

    stat_service = StatService(
        request.app.config, request.app.db, request.app.cache)
    user['stat'] = await stat_service.user_stat_info_by_user_id(user['id'])

    return UserSchema().dump(user)


async def dump_user_infos(request, users):
    if not users:
        return []

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    files = await storage_service.file_infos([v['avatar_id'] for v in users])
    for user, file in zip(users, files):
        user['avatar'] = file

    stat_service = StatService(
        request.app.config, request.app.db, request.app.cache)
    stats = await stat_service.user_stat_infos_by_user_ids(
        [v['id'] for v in users])
    for user, stat in zip(users, stats):
        user['stat'] = stat

    return [UserSchema().dump(v) for v in users]


async def dump_post_info(request, post):
    if post is None:
        return None

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    user = await user_service.info(post['user_id'])

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    user['avatar'] = await storage_service.file_info(user['avatar_id'])

    post['user'] = user

    post['image_ids'] = post['image_ids'] or []
    post['images'] = await storage_service.file_infos(post['image_ids'])

    post['video'] = await storage_service.file_info(post['video_id'])

    stat_service = StatService(
        request.app.config, request.app.db, request.app.cache)
    post['stat'] = await stat_service.post_stat_info_by_post_id(post['id'])

    return PostSchema().dump(post)


async def dump_post_infos(request, posts):
    if not posts:
        return []

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    users = await user_service.infos([v['user_id'] for v in posts])

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    files = await storage_service.file_infos([v['avatar_id'] for v in users])
    for user, file in zip(users, files):
        user['avatar'] = file

    for post, user in zip(posts, users):
        post['user'] = user

    for post in posts:
        post['image_ids'] = post['image_ids'] or []
    images = await storage_service.file_infos(
        [image_id for post in posts for image_id in post['image_ids']])
    start = 0
    for post in posts:
        length = len(post['image_ids'])
        post['images'] = images[start:start+length]
        start += length

    files = await storage_service.file_infos([v['video_id'] for v in posts])
    for post, file in zip(posts, files):
        post['video'] = file

    stat_service = StatService(
        request.app.config, request.app.db, request.app.cache)
    stats = await stat_service.post_stat_infos_by_post_ids(
        [v['id'] for v in posts])
    for post, stat in zip(posts, stats):
        post['stat'] = stat

    return [PostSchema().dump(v) for v in posts]
