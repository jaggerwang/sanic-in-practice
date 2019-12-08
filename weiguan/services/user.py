import string

import sqlalchemy.sql as sasql

from ..utils import random_string, sha256_hash
from ..dependencies import UserRepo, UserFollowRepo
from .common import UsecaseException, NotFoundException


class UserService:
    _mobile_verify_codes = {}
    _email_verify_codes = {}

    def __init__(self, config: dict, user_repo: UserRepo,
                 user_follow_repo: UserFollowRepo):
        self.config = config
        self.user_repo = user_repo
        self.user_follow_repo = user_follow_repo

    async def create_user(self, **data):
        if (await self.info_by_username(data['username'])) is not None:
            raise UsecaseException("用户名重复")

        data['salt'] = random_string(64)
        data['password'] = sha256_hash(data['password'], data['salt'])

        return await self.user_repo.create(**data)

    async def modify_user(self, id, **data):
        if data.get('username') is not None and (await self.info_by_username(data['username'])) is not None:
            raise UsecaseException("用户名重复")

        if data.get('mobile') is not None and (await self.info_by_mobile(data['mobile'])) is not None:
            raise UsecaseException("手机重复")

        if data.get('email') is not None and (await self.info_by_email(data['email'])) is not None:
            raise UsecaseException("邮箱重复")

        if data.get('password') is not None:
            user = self.info(id)
            data['password'] = sha256_hash(data['password'], user['salt'])

        return await self.user_repo.modify(id, **data)

    async def info(self, id):
        if id is None:
            return None

        user = await self.user_repo.info(id)
        if user is None:
            raise NotFoundException('用户未找到')

        return user

    async def info_by_username(self, username):
        return await self.user_repo.info(username, 'username')

    async def info_by_mobile(self, mobile):
        return await self.user_repo.info(mobile, 'mobile')

    async def info_by_email(self, email):
        return await self.user_repo.info(email, 'email')

    async def infos(self, ids):
        return await self.user_repo.infos(ids)

    async def list(self, *, limit=None, offset=None):
        return await self.user_repo.list(limit=limit, offset=offset)

    async def follow(self, follower_id, following_id):
        return await self.user_follow_repo.create(
            follower_id=follower_id, following_id=following_id)

    async def unfollow(self, follower_id, following_id):
        await self.user_follow_repo.execute(
            sasql.delete(self.user_follow_repo.table).
            where(sasql.and_(
                self.user_follow_repo.table.c.follower_id == follower_id,
                self.user_follow_repo.table.c.following_id == following_id)))

    async def following(self, user_id, limit=None, offset=None):
        from_ = self.user_repo.table.join(
            self.user_follow_repo.table,
            self.user_follow_repo.table.c.following_id == self.user_repo.table.c.id)

        where = self.user_follow_repo.table.c.follower_id == user_id

        order_by = self.user_follow_repo.table.c.id.desc()

        return await self.user_repo.list(
            from_=from_, where=where, order_by=order_by, limit=limit,
            offset=offset)

    async def follower(self, user_id, limit=None, offset=None):
        from_ = self.user_repo.table.join(
            self.user_follow_repo.table,
            self.user_follow_repo.table.c.follower_id == self.user_repo.table.c.id)

        where = self.user_follow_repo.table.c.following_id == user_id

        order_by = self.user_follow_repo.table.c.id.desc()

        return await self.user_repo.list(
            from_=from_, where=where, order_by=order_by, limit=limit,
            offset=offset)

    async def is_following_users(self, follower_id, following_ids):
        valid_ids = [v for v in following_ids if v is not None]
        if valid_ids:
            result = await self.user_follow_repo.execute(
                self.user_follow_repo.table.select()
                .where(sasql.and_(
                    self.user_follow_repo.table.c.follower_id == follower_id,
                    self.user_follow_repo.table.c.following_id.in_(following_ids))))
            d = {v['following_id']: True for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v, False) for v in following_ids]

    async def send_mobile_verify_code(self, type, mobile):
        key = '{}_{}'.format(type, mobile)
        code = self._mobile_verify_codes.get(key)
        if code is None:
            code = random_string(6, string.digits)
            # 模拟发送，实际应调用第三方 API 来发送验证码短信
            self._mobile_verify_codes[key] = code

        return code

    async def check_mobile_verify_code(self, type, mobile, code):
        key = '{}_{}'.format(type, mobile)
        sended = self._mobile_verify_codes.get(key)
        if sended is None or sended != code:
            return False

        del self._mobile_verify_codes[key]

        return True

    async def send_email_verify_code(self, type, email):
        key = '{}_{}'.format(type, email)
        code = self._email_verify_codes.get(key)
        if code is None:
            code = random_string(6, string.digits)
            self._email_verify_codes[key] = code

            # TODO 调用第三方 API 发送验证码邮件

        return code

    async def check_email_verify_code(self, type, email, code):
        key = '{}_{}'.format(type, email)
        sended = self._email_verify_codes.get(key)
        if sended is None or sended != code:
            return False

        del self._email_verify_codes[key]

        return True
