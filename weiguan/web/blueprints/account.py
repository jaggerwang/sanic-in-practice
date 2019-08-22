from sanic import Blueprint

from ...utils import sha256_hash
from ...container import Container
from ...entities import UserSchema
from .common import response_json, ResponseCode, authenticated, dump_user_info

account = Blueprint('account', url_prefix='/account')


@account.post('/register')
async def register(request):
    data = request.json
    username = data['username']
    password = data['password']

    user_service = Container().user_service
    user = await user_service.create_user(username=username, password=password)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@account.post('/login')
async def login(request):
    data = request.json
    username = data.get('username')
    mobile = data.get('mobile')
    password = data['password']

    user_service = Container().user_service
    if username is not None:
        user = await user_service.info_by_username(username)
    elif mobile is not None:
        user = await user_service.info_by_mobile(mobile)
    else:
        user = None

    if (user is None or
            sha256_hash(password, user['salt']) != user['password']):
        return response_json(ResponseCode.FAIL, '帐号或密码错误')

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@account.get('/logout')
async def logout(request):
    user = request['session'].pop('user', None)

    return response_json(user=user)


@account.get('/info')
async def info(request):
    user = request['session'].get('user')

    return response_json(user=user)


@account.post('/modify')
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
        return response_json(ResponseCode.FAIL, '验证码错误')

    user = await user_service.modify_user(
        user_id, username=username, password=password, mobile=mobile,
        email=email, avatar_id=avatar_id, intro=intro)

    request['session']['user'] = await dump_user_info(user)

    return response_json(user=request['session']['user'])


@account.post('/send/mobile/verify/code')
async def send_mobile_verify_code(request):
    data = request.json
    type = data['type']
    mobile = data['mobile']

    user_service = Container().user_service
    code = await user_service.send_mobile_verify_code(type, mobile)

    return response_json(verifyCode=code)
