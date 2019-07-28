import string

import sqlalchemy.sql as sasql

from ..utils import random_string, sha256_hash
from ..models import UserModel


class UserService(object):
    mobile_verify_codes = {}
    email_verify_codes = {}

    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    async def create(self, **data):
        data['salt'] = random_string(64)
        data['password'] = sha256_hash(data['password'], data['salt'])

        async with self.db.acquire() as conn:
            result = await conn.execute(sasql.insert(UserModel).values(**data))
            id = result.lastrowid

        return await self.info(id)

    async def edit(self, id, **data):
        data = {k: v for k, v in data.items() if v is not None}

        if 'password' in data:
            user = self.info(id)
            data['password'] = sha256_hash(data['password'], user['salt'])

        async with self.db.acquire() as conn:
            await conn.execute(
                sasql.update(UserModel).where(UserModel.c.id == id).
                values(**data))

        return await self.info(id)

    async def info(self, id):
        async with self.db.acquire() as conn:
            result = await conn.execute(
                UserModel.select().where(UserModel.c.id == id))
            row = await result.first()

        return None if row is None else dict(row)

    async def info_by_username(self, username):
        async with self.db.acquire() as conn:
            result = await conn.execute(
                UserModel.select().where(UserModel.c.username == username))
            row = await result.first()

        return None if row is None else dict(row)

    async def info_by_mobile(self, mobile):
        async with self.db.acquire() as conn:
            result = await conn.execute(
                UserModel.select().where(UserModel.c.mobile == mobile))
            row = await result.first()

        return None if row is None else dict(row)

    async def infos(self, ids):
        if not ids:
            return []

        async with self.db.acquire() as conn:
            result = await conn.execute(
                UserModel.select().where(UserModel.c.id.in_(ids)))
            d = {v['id']: dict(v) for v in await result.fetchall()}

        return [d.get(v) for v in ids]

    async def list_(self, *, limit=None, offset=None):
        select_sm = UserModel.select()
        count_sm = sasql.select([sasql.func.count()]).\
            select_from(UserModel)

        select_sm = select_sm.order_by(UserModel.c.id.desc())

        if limit is not None:
            select_sm = select_sm.limit(limit)
        if offset is not None:
            select_sm = select_sm.offset(offset)

        async with self.db.acquire() as conn:
            result = await conn.execute(select_sm)
            rows = [dict(v) for v in await result.fetchall()]

            result = await conn.execute(count_sm)
            total = await result.scalar()

        return (rows, total)

    async def send_mobile_verify_code(self, type, mobile):
        key = '{}_{}'.format(type, mobile)
        code = self.mobile_verify_codes.get(key)
        if code is None:
            code = random_string(6, string.digits)
            self.mobile_verify_codes[key] = code

            # TODO 调用第三方 API 发送验证码短信

        return code

    async def check_mobile_verify_code(self, type, mobile, code):
        key = '{}_{}'.format(type, mobile)
        sended = self.mobile_verify_codes.get(key)
        if sended is None or sended != code:
            return False

        del self.mobile_verify_codes[key]

        return True

    async def send_email_verify_code(self, type, email):
        key = '{}_{}'.format(type, email)
        code = self.email_verify_codes.get(key)
        if code is None:
            code = random_string(6, string.digits)
            self.email_verify_codes[key] = code

            # TODO 调用第三方 API 发送验证码邮件

        return code

    async def check_email_verify_code(self, type, email, code):
        key = '{}_{}'.format(type, email)
        sended = self.email_verify_codes.get(key)
        if sended is None or sended != code:
            return False

        del self.email_verify_codes[key]

        return True
