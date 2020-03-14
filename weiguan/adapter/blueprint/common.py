import traceback
from functools import wraps

from sanic import response
from sanic.exceptions import SanicException
from pymysql.err import IntegrityError

from .schema import PostSchema, UserSchema, PostStatSchema, UserStatSchema
from ...container import Container
from ...usecase import UsecaseException, UnauthenticatedException, \
    UnauthorizedException, NotFoundException


def response_json(code='ok', message='', status=200, **data):
    return response.json({'code': code, 'message': message, 'data': data},
                         status)


def handle_exception(request, e):
    status = 200
    code = 'fail'
    message = repr(e)
    if isinstance(e, SanicException):
        if e.status_code is not None:
            status = e.status_code
        traceback.print_exc()
    elif isinstance(e, UsecaseException):
        message = e.message
        if isinstance(e, UnauthenticatedException):
            status = 401
            code = 'unauthenticated'
        elif isinstance(e, UnauthorizedException):
            status = 403
            code = 'unauthorized'
        elif isinstance(e, NotFoundException):
            status = 404
            code = 'not_found'
    else:
        traceback.print_exc()

    return response_json(code, message, status)


def authenticated():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request['session'].get('user') is None:
                raise UnauthenticatedException('未认证')

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator


async def dump_user_info(user, user_id=None):
    if user is None:
        return None

    file_usecase = Container().file_usecase
    user['avatar'] = await file_usecase.info(user['avatar_id'])

    user = UserSchema().dump(user)

    stat_usecase = Container().stat_usecase
    stat = await stat_usecase.user_stat_info_by_user_id(user['id'])
    if stat is not None:
        stat = UserStatSchema().dump(stat)
    user['stat'] = stat

    if user_id is not None:
        user_usecase = Container().user_usecase
        user['following'] = (await user_usecase.is_following_users(
            user_id, [user['id']]))[0]

    return user


async def dump_user_infos(users, user_id=None):
    if not users:
        return []

    file_usecase = Container().file_usecase
    files = await file_usecase.infos([v['avatar_id'] for v in users])
    for user, file in zip(users, files):
        user['avatar'] = file

    users = [UserSchema().dump(v) for v in users]

    stat_usecase = Container().stat_usecase
    stats = await stat_usecase.user_stat_infos_by_user_ids(
        [v['id'] for v in users])
    for user, stat in zip(users, stats):
        if stat is not None:
            stat = UserStatSchema().dump(stat)
        user['stat'] = stat

    if user_id is not None:
        user_usecase = Container().user_usecase
        is_followginss = await user_usecase.is_following_users(
            user_id, [v['id'] for v in users])
        for user, is_followgins in zip(users, is_followginss):
            user['following'] = is_followgins

    return users


async def dump_post_info(post, user_id=None):
    if post is None:
        return None

    user_usecase = Container().user_usecase
    user = await user_usecase.info(post['user_id'])

    file_usecase = Container().file_usecase
    user['avatar'] = await file_usecase.info(user['avatar_id'])

    post['user'] = user

    post['image_ids'] = post['image_ids'] or []
    post['images'] = await file_usecase.infos(post['image_ids'])

    post['video'] = await file_usecase.info(post['video_id'])

    post = PostSchema().dump(post)

    stat_usecase = Container().stat_usecase
    stat = await stat_usecase.post_stat_info_by_post_id(post['id'])
    if stat is not None:
        stat = PostStatSchema().dump(stat)
    post['stat'] = stat

    if user_id is not None:
        post_usecase = Container().post_usecase
        post['liked'] = (await post_usecase.is_liked_posts(
            user_id, [post['id']]))[0]

    return post


async def dump_post_infos(posts, user_id=None):
    if not posts:
        return []

    user_usecase = Container().user_usecase
    users = await user_usecase.infos([v['user_id'] for v in posts])

    file_usecase = Container().file_usecase
    files = await file_usecase.infos([v['avatar_id'] for v in users])
    for user, file in zip(users, files):
        user['avatar'] = file

    for post, user in zip(posts, users):
        post['user'] = user

    for post in posts:
        post['image_ids'] = post['image_ids'] or []
    images = await file_usecase.infos(
        [image_id for post in posts for image_id in post['image_ids']])
    start = 0
    for post in posts:
        length = len(post['image_ids'])
        post['images'] = images[start:start+length]
        start += length

    files = await file_usecase.infos([v['video_id'] for v in posts])
    for post, file in zip(posts, files):
        post['video'] = file

    posts = [PostSchema().dump(v) for v in posts]

    stat_usecase = Container().stat_usecase
    stats = await stat_usecase.post_stat_infos_by_post_ids(
        [v['id'] for v in posts])
    for post, stat in zip(posts, stats):
        if stat is not None:
            stat = PostStatSchema().dump(stat)
        post['stat'] = stat

    if user_id is not None:
        post_usecase = Container().post_usecase
        is_likeds = await post_usecase.is_liked_posts(
            user_id, [v['id'] for v in posts])
        for post, is_liked in zip(posts, is_likeds):
            post['liked'] = is_liked

    return posts
