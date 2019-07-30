import os
import hashlib

import sqlalchemy.sql as sasql

from ..models import UserStatModel, PostStatModel, UserModel, PostModel, \
    PostLikeModel, UserFollowModel


class StatService:
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    async def stat_user(self, user_id):
        async with self.db.acquire() as conn:
            data = {
                'post_count': 0,
                'like_count': 0,
                'following_count': 0,
                'follower_count': 0,
            }

            result = await conn.execute(
                sasql.select([sasql.func.count()]).
                select_from(PostModel).
                where(PostModel.c.user_id == user_id))
            data['post_count'] = await result.scalar()

            result = await conn.execute(
                sasql.select([sasql.func.count()]).
                select_from(PostLikeModel).
                where(PostLikeModel.c.user_id == user_id))
            data['like_count'] = await result.scalar()

            result = await conn.execute(
                sasql.select([sasql.func.count()]).
                select_from(UserFollowModel).
                where(UserFollowModel.c.follower_id == user_id))
            data['following_count'] = await result.scalar()

            result = await conn.execute(
                sasql.select([sasql.func.count()]).
                select_from(UserFollowModel).
                where(UserFollowModel.c.following_id == user_id))
            data['follower_count'] = await result.scalar()

            result = await conn.execute(
                UserStatModel.select().
                where(UserStatModel.c.user_id == user_id))
            row = await result.first()
            if row is None:
                await conn.execute(
                    sasql.insert(UserStatModel).values(user_id=user_id, **data))
            else:
                await conn.execute(
                    sasql.update(UserStatModel).
                    where(UserStatModel.c.user_id == user_id).values(**data))

        return await self.user_stat_info_by_user_id(user_id)

    async def stat_all_users(self):
        async with self.db.acquire() as conn:
            result = await conn.execute(UserModel.select())
            user_ids = [v['id'] for v in await result.fetchall()]

        for user_id in user_ids:
            await self.stat_user(user_id)

    async def user_stat_info_by_user_id(self, user_id):
        if user_id is None:
            return None

        async with self.db.acquire() as conn:
            result = await conn.execute(
                UserStatModel.select().
                where(UserStatModel.c.user_id == user_id))
            row = await result.first()

        return None if row is None else dict(row)

    async def user_stat_infos_by_user_ids(self, user_ids):
        valid_ids = [v for v in user_ids if v is not None]
        if valid_ids:
            async with self.db.acquire() as conn:
                result = await conn.execute(
                    UserStatModel.select().
                    where(UserStatModel.c.user_id.in_(valid_ids)))
                d = {v['user_id']: dict(v) for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v) for v in user_ids]

    async def stat_post(self, post_id):
        async with self.db.acquire() as conn:
            data = {
                'like_count': 0,
            }

            result = await conn.execute(
                sasql.select([sasql.func.count()]).
                select_from(PostLikeModel).
                where(PostLikeModel.c.post_id == post_id))
            data['like_count'] = await result.scalar()

            result = await conn.execute(
                PostStatModel.select().
                where(PostStatModel.c.post_id == post_id))
            row = await result.first()
            if row is None:
                await conn.execute(
                    sasql.insert(PostStatModel).values(post_id=post_id, **data))
            else:
                await conn.execute(
                    sasql.update(PostStatModel).
                    where(PostStatModel.c.post_id == post_id).values(**data))

        return await self.post_stat_info_by_post_id(post_id)

    async def stat_all_posts(self):
        async with self.db.acquire() as conn:
            result = await conn.execute(PostModel.select())
            post_ids = [v['id'] for v in await result.fetchall()]

        for post_id in post_ids:
            await self.stat_post(post_id)

    async def post_stat_info_by_post_id(self, post_id):
        if post_id is None:
            return None

        async with self.db.acquire() as conn:
            result = await conn.execute(
                PostStatModel.select().
                where(PostStatModel.c.post_id == post_id))
            row = await result.first()

        return None if row is None else dict(row)

    async def post_stat_infos_by_post_ids(self, post_ids):
        valid_ids = [v for v in post_ids if v is not None]
        if valid_ids:
            async with self.db.acquire() as conn:
                result = await conn.execute(
                    PostStatModel.select().
                    where(PostStatModel.c.post_id.in_(valid_ids)))
                d = {v['post_id']: dict(v) for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v) for v in post_ids]
