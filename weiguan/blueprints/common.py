from enum import Enum
import traceback
from functools import wraps

from sanic import response
from sanic.exceptions import SanicException, Unauthorized

from ..models import PostSchema, UserSchema
from ..services import ServiceException, StorageService, UserService


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


async def dump_post_info(request, post):
    if post is None:
        return None

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    post['user'] = await user_service.info(post['user_id'])

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    if post['image_ids'] is not None:
        post['images'] = await storage_service.file_infos(post['image_ids'])

    if post['video_id'] is not None:
        post['video'] = await storage_service.file_info(post['video_id'])

    return PostSchema().dump(post)


async def dump_post_infos(request, posts):
    if not posts:
        return []

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    users = await user_service.infos([v['user_id'] for v in posts])
    for post, user in zip(posts, users):
        post['user'] = user

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    image_posts = [v for v in posts if v['image_ids'] is not None]
    images = await storage_service.file_infos(
        [image_id for post in image_posts for image_id in post['image_ids']])
    start = 0
    for post in image_posts:
        length = len(post['image_ids'])
        post['images'] = images[start:start+length]
        start += length

    video_posts = [v for v in posts if v['video_id'] is not None]
    files = await storage_service.file_infos(
        [v['video_id'] for v in video_posts])
    for post, file in zip(video_posts, files):
        post['video'] = file

    return [PostSchema().dump(v) for v in posts]
