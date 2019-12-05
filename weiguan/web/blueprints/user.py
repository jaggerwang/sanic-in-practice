import re

from sanic import Blueprint

from ...utils import sha256_hash
from ...container import Container
from ...entities import UserSchema
from ...services import UsecaseException
from .common import response_json, authenticated, dump_user_info, dump_user_infos

user = Blueprint('user', url_prefix='/user')


@user.post('/register')
async def register(request):
    data = request.json
    username = data['username']
    password = data['password']

    user_service = Container().user_service
    user = await user_service.create_user(username=username, password=password)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user.post('/login')
async def login(request):
    data = request.json
    username = data.get('username')
    password = data['password']

    user_service = Container().user_service
    if re.match('^\d+$', username):
        user = await user_service.info_by_mobile(username)
    else:
        user = await user_service.info_by_username(username)

    if (user is None or
            sha256_hash(password, user['salt']) != user['password']):
        raise UsecaseException('用户名或密码错误')

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user.get('/logged')
async def logged(request):
    user = request['session'].get('user')

    return response_json(user=user)


@user.get('/logout')
@authenticated()
async def logout(request):
    user = request['session'].pop('user', None)

    return response_json(user=user)


@user.post('/modify')
@authenticated()
async def modify(request):
    user_id = request['session']['user']['id']

    data = request.json
    username = data.get('username')
    password = data.get('password')
    mobile = data.get('mobile')
    email = data.get('email')
    avatar_id = data.get('avatarId')
    intro = data.get('intro')
    code = data.get('code')

    user_service = Container().user_service

    if ((mobile is not None and
            not (await user_service.check_mobile_verify_code('modify', mobile, code))) or
            (email is not None and
             not (await user_service.check_email_verify_code('modify', email, code)))):
        raise UsecaseException('验证码错误')

    user = await user_service.modify_user(
        user_id, username=username, password=password, mobile=mobile,
        email=email, avatar_id=avatar_id, intro=intro)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user.get('/info')
@authenticated()
async def info(request):
    user_id = request['session']['user']['id']

    id = request.args.get('id')
    if id is not None:
        id = int(id)

    user_service = Container().user_service
    user = await user_service.info(id)

    return response_json(user=await dump_user_info(user, user_id))


@user.post('/follow')
@authenticated()
async def follow(request):
    user_id = request['session']['user']['id']

    data = request.json
    following_id = data['followingId']

    user_service = Container().user_service
    await user_service.follow(user_id, following_id)

    return response_json()


@user.post('/unfollow')
@authenticated()
async def unfollow(request):
    user_id = request['session']['user']['id']

    data = request.json
    following_id = data['followingId']

    user_service = Container().user_service
    await user_service.unfollow(user_id, following_id)

    return response_json()


@user.get('/following')
@authenticated()
async def following(request):
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

    user_service = Container().user_service
    users, total = await user_service.following(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        users=await dump_user_infos(users, user_id), total=total)


@user.get('/follower')
@authenticated()
async def follower(request):
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

    user_service = Container().user_service
    users, total = await user_service.follower(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        users=await dump_user_infos(users, user_id), total=total)


@user.post('/sendMobileVerifyCode')
async def send_mobile_verify_code(request):
    data = request.json
    type = data['type']
    mobile = data['mobile']

    user_service = Container().user_service
    code = await user_service.send_mobile_verify_code(type, mobile)

    return response_json(verifyCode=code)
