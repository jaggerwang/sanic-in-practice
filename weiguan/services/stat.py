import os
import hashlib

import sqlalchemy.sql as sasql

from ..dependencies import UserStatRepo, PostStatRepo, UserRepo, UserFollowRepo, \
    PostRepo, PostLikeRepo


class StatService:
    def __init__(self, config: dict, user_stat_repo: UserStatRepo,
                 post_stat_repo: PostStatRepo, user_repo: UserRepo,
                 user_follow_repo: UserFollowRepo, post_repo: PostRepo,
                 post_like_repo: PostLikeRepo):
        self.config = config
        self.user_stat_repo = user_stat_repo
        self.post_stat_repo = post_stat_repo
        self.user_repo = user_repo
        self.user_follow_repo = user_follow_repo
        self.post_repo = post_repo
        self.post_like_repo = post_like_repo

    async def stat_user(self, user_id):
        data = {
            'post_count': 0,
            'like_count': 0,
            'following_count': 0,
            'follower_count': 0,
        }

        result = await self.post_repo.execute(
            sasql.select([sasql.func.count()]).
            select_from(self.post_repo.table).
            where(self.post_repo.table.c.user_id == user_id))
        data['post_count'] = await result.scalar()

        result = await self.post_like_repo.execute(
            sasql.select([sasql.func.count()]).
            select_from(self.post_like_repo.table).
            where(self.post_like_repo.table.c.user_id == user_id))
        data['like_count'] = await result.scalar()

        result = await self.user_follow_repo.execute(
            sasql.select([sasql.func.count()]).
            select_from(self.user_follow_repo.table).
            where(self.user_follow_repo.table.c.follower_id == user_id))
        data['following_count'] = await result.scalar()

        result = await self.user_follow_repo.execute(
            sasql.select([sasql.func.count()]).
            select_from(self.user_follow_repo.table).
            where(self.user_follow_repo.table.c.following_id == user_id))
        data['follower_count'] = await result.scalar()

        result = await self.user_stat_repo.execute(
            self.user_stat_repo.table.select().
            where(self.user_stat_repo.table.c.user_id == user_id))
        row = await result.first()
        if row is None:
            await self.user_stat_repo.execute(
                sasql.insert(self.user_stat_repo.table)
                .values(user_id=user_id, **data))
        else:
            await self.user_stat_repo.execute(
                sasql.update(self.user_stat_repo.table).
                where(self.user_stat_repo.table.c.user_id == user_id)
                .values(**data))

        return await self.user_stat_info_by_user_id(user_id)

    async def stat_all_users(self):
        result = await self.user_repo.execute(self.user_repo.table.select())
        user_ids = [v['id'] for v in await result.fetchall()]

        for user_id in user_ids:
            await self.stat_user(user_id)

    async def user_stat_info_by_user_id(self, user_id):
        return await self.user_stat_repo.info(user_id, 'user_id')

    async def user_stat_infos_by_user_ids(self, user_ids):
        return await self.user_stat_repo.infos(user_ids, 'user_id')

    async def stat_post(self, post_id):
        data = {
            'like_count': 0,
        }

        result = await self.post_like_repo.execute(
            sasql.select([sasql.func.count()]).
            select_from(self.post_like_repo.table).
            where(self.post_like_repo.table.c.post_id == post_id))
        data['like_count'] = await result.scalar()

        result = await self.post_stat_repo.execute(
            self.post_stat_repo.table.select().
            where(self.post_stat_repo.table.c.post_id == post_id))
        row = await result.first()
        if row is None:
            await self.post_stat_repo.execute(
                sasql.insert(self.post_stat_repo.table)
                .values(post_id=post_id, **data))
        else:
            await self.post_stat_repo.execute(
                sasql.update(self.post_stat_repo.table).
                where(self.post_stat_repo.table.c.post_id == post_id)
                .values(**data))

        return await self.post_stat_info_by_post_id(post_id)

    async def stat_all_posts(self):
        result = await self.post_repo.execute(self.post_repo.table.select())
        post_ids = [v['id'] for v in await result.fetchall()]

        for post_id in post_ids:
            await self.stat_post(post_id)

    async def post_stat_info_by_post_id(self, post_id):
        return await self.post_stat_repo.info(post_id, 'post_id')

    async def post_stat_infos_by_post_ids(self, post_ids):
        return await self.post_stat_repo.infos(post_ids, 'post_id')
