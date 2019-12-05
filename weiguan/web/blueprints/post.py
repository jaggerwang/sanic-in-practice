from sanic import Blueprint

from ...utils import sha256_hash
from ...container import Container
from ...entities import PostSchema
from ...services import UnauthorizedException
from .common import response_json, authenticated, dump_post_info, dump_post_infos

post = Blueprint('post', url_prefix='/post')


@post.post('/publish')
@authenticated()
async def publish(request):
    user_id = request['session']['user']['id']

    data = request.json
    type = data['type']
    text = data.get('text', '')
    image_ids = data.get('imageIds')
    video_id = data.get('videoId')

    post_service = Container().post_service
    post = await post_service.create_post(
        user_id=user_id, type=type, text=text, image_ids=image_ids,
        video_id=video_id)

    return response_json(post=await dump_post_info(post))


@post.post('/delete')
@authenticated()
async def delete(request):
    user_id = request['session']['user']['id']

    data = request.json
    id = data['id']

    post_service = Container().post_service
    post = await post_service.info(id)

    if user_id != post['user_id']:
        raise UnauthorizedException('无权删除动态')

    await post_service.delete_post(id)

    return response_json(post=await dump_post_info(post))


@post.get('/info')
@authenticated()
async def info(request):
    user_id = request['session'].get('user', {}).get('id')

    id = request.args.get('id')
    if id is not None:
        id = int(id)

    post_service = Container().post_service
    post = await post_service.info(id)

    return response_json(post=await dump_post_info(post, user_id))


@post.get('/published')
@authenticated()
async def published(request):
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

    post_service = Container().post_service
    posts, total = await post_service.list(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        posts=await dump_post_infos(posts, user_id), total=total)


@post.post('/like')
@authenticated()
async def like(request):
    user_id = request['session']['user']['id']

    data = request.json
    post_id = data['postId']

    post_service = Container().post_service
    await post_service.like(user_id, post_id)

    return response_json()


@post.post('/unlike')
@authenticated()
async def unlike(request):
    user_id = request['session']['user']['id']

    data = request.json
    post_id = data['postId']

    post_service = Container().post_service
    await post_service.unlike(user_id, post_id)

    return response_json()


@post.get('/liked')
@authenticated()
async def liked(request):
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

    post_service = Container().post_service
    posts, total = await post_service.liked(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        posts=await dump_post_infos(posts, user_id), total=total)


@post.get('/following')
@authenticated()
async def following(request):
    user_id = request['session']['user']['id']

    limit = request.args.get('limit')
    if limit is not None:
        limit = int(limit)
    before_id = request.args.get('beforeId')
    if before_id is not None:
        before_id = int(before_id)
    after_id = request.args.get('afterId')
    if after_id is not None:
        after_id = int(after_id)

    post_service = Container().post_service
    posts, total = await post_service.following(
        user_id=user_id, limit=limit, before_id=before_id, after_id=after_id)

    return response_json(
        posts=await dump_post_infos(posts, user_id), total=total)
