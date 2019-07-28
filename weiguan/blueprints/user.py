from sanic import Blueprint
from sanic.exceptions import NotFound

from ..services import UserService
from ..models import UserSchema
from .common import ResponseCode, response_json, authenticated, dump_user_info, \
    dump_user_infos

user = Blueprint('user', url_prefix='/user')


@user.get('/info')
@authenticated()
async def info(request):
    id = int(request.args.get('id'))

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    user = await user_service.info(id)
    if user is None:
        raise NotFound('')

    return response_json(user=await dump_user_info(request, user))


@user.post('/follow')
@authenticated()
async def follow(request):
    user_id = request['session']['user']['id']

    data = request.json
    following_id = data['followingId']

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    await user_service.follow(user_id, following_id)

    return response_json()


@user.post('/unfollow')
@authenticated()
async def unfollow(request):
    user_id = request['session']['user']['id']

    data = request.json
    following_id = data['followingId']

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    await user_service.unfollow(user_id, following_id)

    return response_json()


@user.get('/followings')
@authenticated()
async def followings(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    else:
        user_id = request['session']['user']['id']
    limit = request.args.get('limit')
    if limit is not None:
        limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)
    before_id = request.args.get('beforeId')
    if before_id is not None:
        before_id = int(before_id)
    after_id = request.args.get('afterId')
    if after_id is not None:
        after_id = int(after_id)

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    users, total = await user_service.followings(
        user_id=user_id, limit=limit, offset=offset, before_id=before_id,
        after_id=after_id)

    return response_json(
        users=await dump_user_infos(request, users), total=total)


@user.get('/followers')
@authenticated()
async def followers(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    else:
        user_id = request['session']['user']['id']
    limit = request.args.get('limit')
    if limit is not None:
        limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)
    before_id = request.args.get('beforeId')
    if before_id is not None:
        before_id = int(before_id)
    after_id = request.args.get('afterId')
    if after_id is not None:
        after_id = int(after_id)

    user_service = UserService(
        request.app.config, request.app.db, request.app.cache)
    users, total = await user_service.followers(
        user_id=user_id, limit=limit, offset=offset, before_id=before_id,
        after_id=after_id)

    return response_json(
        users=await dump_user_infos(request, users), total=total)
