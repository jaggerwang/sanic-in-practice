import string

import sqlalchemy.sql as sasql

from ..models import PostType, PostModel, PostLikeModel, UserFollowModel
from .common import ServiceException


class PostService:
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    async def create(self, **data):
        if ((data['type'] == PostType.TEXT.value and not data['text']) or
            (data['type'] == PostType.IMAGE.value and not data['image_ids']) or
                (data['type'] == PostType.VIDEO.value and not data['video_id'])):
            raise ServiceException('内容不能为空')

        async with self.db.acquire() as conn:
            result = await conn.execute(sasql.insert(PostModel).values(**data))
            id = result.lastrowid

        return await self.info(id)

    async def delete(self, id):
        async with self.db.acquire() as conn:
            await conn.execute(
                sasql.delete(PostModel).where(PostModel.c.id == id))

    async def info(self, id):
        if id is None:
            return None

        async with self.db.acquire() as conn:
            result = await conn.execute(
                PostModel.select().where(PostModel.c.id == id))
            row = await result.first()

        return None if row is None else dict(row)

    async def infos(self, ids):
        valid_ids = [v for v in ids if v is not None]
        if valid_ids:
            async with self.db.acquire() as conn:
                result = await conn.execute(
                    PostModel.select().where(PostModel.c.id.in_(valid_ids)))
                d = {v['id']: dict(v) for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v) for v in ids]

    async def list_(self, *, user_id=None, limit=None, offset=None,
                    before_id=None, after_id=None):
        select_sm = PostModel.select()
        count_sm = sasql.select([sasql.func.count()]).\
            select_from(PostModel)

        if user_id is not None:
            clause = PostModel.c.user_id == user_id
            select_sm = select_sm.where(clause)
            count_sm = count_sm.where(clause)

        select_sm = select_sm.order_by(PostModel.c.id.desc())

        if limit is not None:
            select_sm = select_sm.limit(limit)
        if offset is not None:
            select_sm = select_sm.offset(offset)

        if before_id is not None:
            select_sm = select_sm.where(PostModel.c.id < before_id)
        if after_id is not None:
            select_sm = select_sm.where(PostModel.c.id > after_id)

        async with self.db.acquire() as conn:
            result = await conn.execute(select_sm)
            rows = [dict(v) for v in await result.fetchall()]

            result = await conn.execute(count_sm)
            total = await result.scalar()

        return (rows, total)

    async def like(self, user_id, post_id):
        async with self.db.acquire() as conn:
            await conn.execute(
                sasql.insert(PostLikeModel).
                values(user_id=user_id, post_id=post_id))

    async def unlike(self, user_id, post_id):
        async with self.db.acquire() as conn:
            await conn.execute(
                sasql.delete(PostLikeModel).
                where(sasql.and_(
                    PostLikeModel.c.user_id == user_id,
                    PostLikeModel.c.post_id == post_id)))

    async def liked(self, user_id, limit=None, offset=None,
                    before_id=None, after_id=None):
        select_sm = sasql.select([PostModel]).\
            select_from(PostModel.join(PostLikeModel)).\
            where(PostLikeModel.c.user_id == user_id)
        count_sm = sasql.select([sasql.func.count()]).\
            select_from(PostLikeModel).\
            where(PostLikeModel.c.user_id == user_id)

        select_sm = select_sm.order_by(PostLikeModel.c.id.desc())

        if limit is not None:
            select_sm = select_sm.limit(limit)
        if offset is not None:
            select_sm = select_sm.offset(offset)

        if before_id is not None:
            select_sm = select_sm.where(PostLikeModel.c.id < before_id)
        if after_id is not None:
            select_sm = select_sm.where(PostLikeModel.c.id > after_id)

        async with self.db.acquire() as conn:
            result = await conn.execute(select_sm)
            rows = [dict(v) for v in await result.fetchall()]

            result = await conn.execute(count_sm)
            total = await result.scalar()

        return (rows, total)

    async def following(self, user_id, limit=None, offset=None,
                        before_id=None, after_id=None):
        from_clause = PostModel.join(
            UserFollowModel,
            PostModel.c.user_id == UserFollowModel.c.following_id)
        where_clause = UserFollowModel.c.follower_id == user_id
        select_sm = sasql.select([PostModel]).\
            select_from(from_clause).\
            where(where_clause)
        count_sm = sasql.select([sasql.func.count()]).\
            select_from(from_clause).\
            where(where_clause)

        select_sm = select_sm.order_by(PostModel.c.id.desc())

        if limit is not None:
            select_sm = select_sm.limit(limit)
        if offset is not None:
            select_sm = select_sm.offset(offset)

        if before_id is not None:
            select_sm = select_sm.where(PostModel.c.id < before_id)
        if after_id is not None:
            select_sm = select_sm.where(PostModel.c.id > after_id)

        async with self.db.acquire() as conn:
            result = await conn.execute(select_sm)
            rows = [dict(v) for v in await result.fetchall()]

            result = await conn.execute(count_sm)
            total = await result.scalar()

        return (rows, total)
