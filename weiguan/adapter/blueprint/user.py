import re

from sanic import Blueprint

from .schema import UserSchema
from ...util import sha256_hash
from ...container import Container
from ...usecase import UsecaseException
from .common import response_json, authenticated, dump_user_info, dump_user_infos

user_blueprint = Blueprint('user', url_prefix='/user')


@user_blueprint.post('/register')
async def register(request):
    data = request.json
    username = data['username']
    password = data['password']

    user_usecase = Container().user_usecase
    user = await user_usecase.create_user(username=username, password=password)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user_blueprint.post('/login')
async def login(request):
    data = request.json
    username = data.get('username')
    password = data['password']

    user_usecase = Container().user_usecase
    if re.match('^\d+$', username):
        user = await user_usecase.info_by_mobile(username)
    else:
        user = await user_usecase.info_by_username(username)

    if (user is None or
            sha256_hash(password, user['salt']) != user['password']):
        raise UsecaseException('用户名或密码错误')

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user_blueprint.get('/logged')
async def logged(request):
    user = request['session'].get('user')

    return response_json(user=user)


@user_blueprint.get('/logout')
@authenticated()
async def logout(request):
    user = request['session'].pop('user', None)

    return response_json(user=user)


@user_blueprint.post('/modify')
@authenticated()
async def modify(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    user = data['user']
    username = user.get('username')
    password = user.get('password')
    mobile = user.get('mobile')
    email = user.get('email')
    avatar_id = user.get('avatarId')
    intro = user.get('intro')
    code = data.get('code')

    user_usecase = Container().user_usecase

    if ((mobile is not None and
            not (await user_usecase.check_mobile_verify_code('modify', mobile, code))) or
            (email is not None and
             not (await user_usecase.check_email_verify_code('modify', email, code)))):
        raise UsecaseException('验证码错误')

    user = await user_usecase.modify_user(
        logged_user_id, username=username, password=password, mobile=mobile,
        email=email, avatar_id=avatar_id, intro=intro)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@user_blueprint.get('/info')
@authenticated()
async def info(request):
    logged_user_id = request['session']['user']['id']

    id = request.args.get('id')
    if id is not None:
        id = int(id)

    user_usecase = Container().user_usecase
    user = await user_usecase.info(id)

    return response_json(user=await dump_user_info(user, logged_user_id))


@user_blueprint.post('/follow')
@authenticated()
async def follow(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    user_id = data['userId']

    user_usecase = Container().user_usecase
    await user_usecase.follow(logged_user_id, user_id)

    return response_json()


@user_blueprint.post('/unfollow')
@authenticated()
async def unfollow(request):
    logged_user_id = request['session']['user']['id']

    data = request.json
    user_id = data['userId']

    user_usecase = Container().user_usecase
    await user_usecase.unfollow(logged_user_id, user_id)

    return response_json()


@user_blueprint.get('/following')
@authenticated()
async def following(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    limit = request.args.get('limit', '20')
    limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)

    user_usecase = Container().user_usecase
    users, total = await user_usecase.following(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        users=await dump_user_infos(users, user_id), total=total)


@user_blueprint.get('/follower')
@authenticated()
async def follower(request):
    user_id = request.args.get('userId')
    if user_id is not None:
        user_id = int(user_id)
    limit = request.args.get('limit', '20')
    limit = int(limit)
    offset = request.args.get('offset')
    if offset is not None:
        offset = int(offset)

    user_usecase = Container().user_usecase
    users, total = await user_usecase.follower(
        user_id=user_id, limit=limit, offset=offset)

    return response_json(
        users=await dump_user_infos(users, user_id), total=total)


@user_blueprint.post('/sendMobileVerifyCode')
async def send_mobile_verify_code(request):
    data = request.json
    type = data['type']
    mobile = data['mobile']

    user_usecase = Container().user_usecase
    code = await user_usecase.send_mobile_verify_code(type, mobile)

    return response_json(verifyCode=code)
