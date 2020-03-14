from sanic import Blueprint

from .schema import PostSchema
from ...util import sha256_hash
from ...container import Container
from ...usecase import UnauthorizedException
from .common import response_json, authenticated, dump_post_info, dump_post_infos

post_blueprint = Blueprint('post', url_prefix='/post')


@post_blueprint.post('/publish')
@authenticated()
async def publish(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    type = data['type']
    text = data.get('text', '')
    image_ids = data.get('imageIds')
    video_id = data.get('videoId')

    post_usecase = Container().post_usecase
    post = await post_usecase.create_post(
        user_id=logged_user_id, type=type, text=text, image_ids=image_ids,
        video_id=video_id)

    return response_json(post=await dump_post_info(post))


@post_blueprint.post('/delete')
@authenticated()
async def delete(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    id = data['id']

    post_usecase = Container().post_usecase
    post = await post_usecase.info(id)

    if logged_user_id != post['user_id']:
        raise UnauthorizedException('无权删除动态')

    await post_usecase.delete_post(id)

    return response_json(post=await dump_post_info(post))


@post_blueprint.get('/info')
@authenticated()
async def info(request):
    logged_user_id = request['session'].get('user', {}).get('id')

    id = request.args.get('id')
    if id is not None:
        id = int(id)

    post_usecase = Container().post_usecase
    post = await post_usecase.info(id)

    return response_json(post=await dump_post_info(post, logged_user_id))


@post_blueprint.get('/published')
@authenticated()
async def published(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    limit = request.args.get('limit', '10')
    limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)

    post_usecase = Container().post_usecase
    posts, total = await post_usecase.list(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        posts=await dump_post_infos(posts, user_id), total=total)


@post_blueprint.post('/like')
@authenticated()
async def like(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    post_id = data['postId']

    post_usecase = Container().post_usecase
    await post_usecase.like(logged_user_id, post_id)

    return response_json()


@post_blueprint.post('/unlike')
@authenticated()
async def unlike(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    post_id = data['postId']

    post_usecase = Container().post_usecase
    await post_usecase.unlike(logged_user_id, post_id)

    return response_json()


@post_blueprint.get('/liked')
@authenticated()
async def liked(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    limit = request.args.get('limit', '10')
    limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)

    post_usecase = Container().post_usecase
    posts, total = await post_usecase.liked(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        posts=await dump_post_infos(posts, user_id), total=total)


@post_blueprint.get('/following')
@authenticated()
async def following(request):
    logged_user_id = request['session']['user']['id']

    limit = request.args.get('limit', '10')
    limit = int(limit)
    before_id = request.args.get('beforeId')
    if before_id is not None:
        before_id = int(before_id)
    after_id = request.args.get('afterId')
    if after_id is not None:
        after_id = int(after_id)

    post_usecase = Container().post_usecase
    posts, total = await post_usecase.following(
        user_id=logged_user_id, limit=limit, before_id=before_id, after_id=after_id)

    return response_json(
        posts=await dump_post_infos(posts, logged_user_id), total=total)
