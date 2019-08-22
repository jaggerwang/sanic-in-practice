import string

import sqlalchemy.sql as sasql

from ..entities import PostType
from ..dependencies import PostRepo, PostLikeRepo, UserFollowRepo
from .common import ServiceException


class PostService:
    def __init__(self, config: dict, post_repo: PostRepo,
                 post_like_repo: PostLikeRepo, user_follow_repo: UserFollowRepo):
        self.config = config
        self.post_repo = post_repo
        self.post_like_repo = post_like_repo
        self.user_follow_repo = user_follow_repo

    async def create_post(self, **data):
        if ((data['type'] == PostType.TEXT.value and not data['text']) or
            (data['type'] == PostType.IMAGE.value and not data['image_ids']) or
                (data['type'] == PostType.VIDEO.value and not data['video_id'])):
            raise ServiceException('内容不能为空')

        return await self.post_repo.create(**data)

    async def delete_post(self, id):
        return await self.post_repo.delete(id)

    async def info(self, id):
        return await self.post_repo.info(id)

    async def infos(self, ids):
        return await self.post_repo.infos(ids)

    async def list(self, *, user_id=None, limit=None, offset=None):
        where = []
        if user_id is not None:
            where.append(self.post_repo.table.c.user_id == user_id)
        where = sasql.and_(*where) if where else None

        order_by = self.post_repo.table.c.id.desc()

        return await self.post_repo.list(
            where=where, order_by=order_by, limit=limit, offset=offset)

    async def like(self, user_id, post_id):
        return await self.post_like_repo.create(
            user_id=user_id, post_id=post_id)

    async def unlike(self, user_id, post_id):
        result = await self.post_like_repo.execute(
            sasql.delete(self.post_like_repo.table).
            where(sasql.and_(
                self.post_like_repo.table.c.user_id == user_id,
                self.post_like_repo.table.c.post_id == post_id)))

        return result.rowcount

    async def liked(self, user_id, limit=None, offset=None):
        from_ = self.post_repo.table.join(self.post_like_repo.table)
        where = self.post_like_repo.table.c.user_id == user_id

        order_by = self.post_like_repo.table.c.id.desc()

        return await self.post_repo.list(
            from_=from_, where=where, order_by=order_by, limit=limit,
            offset=offset)

    async def is_liked_posts(self, user_id, post_ids):
        valid_ids = [v for v in post_ids if v is not None]
        if valid_ids:
            result = await self.post_like_repo.execute(
                self.post_like_repo.table.select()
                .where(sasql.and_(
                    self.post_like_repo.table.c.user_id == user_id,
                    self.post_like_repo.table.c.post_id.in_(post_ids),
                )))
            d = {v['post_id']: True for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v, False) for v in post_ids]

    async def following(self, user_id, limit=None, before_id=None,
                        after_id=None):
        from_ = self.post_repo.table.join(
            self.user_follow_repo.table,
            self.post_repo.table.c.user_id == self.user_follow_repo.table.c.following_id)
        where = self.user_follow_repo.table.c.follower_id == user_id
        select_sm = self.post_repo.table.select()\
            .select_from(from_)\
            .where(where)
        count_sm = sasql.select([sasql.func.count()])\
            .select_from(from_)\
            .where(where)

        if after_id is not None:
            order_by = self.post_repo.table.c.id
        else:
            order_by = self.post_repo.table.c.id.desc()
        select_sm = select_sm.order_by(order_by)

        if limit is not None:
            select_sm = select_sm.limit(limit)

        if before_id is not None:
            select_sm = select_sm.where(self.post_repo.table.c.id < before_id)
        elif after_id is not None:
            select_sm = select_sm.where(self.post_repo.table.c.id > after_id)

        result = await self.post_repo.execute(select_sm)
        rows = [dict(v) for v in await result.fetchall()]

        result = await self.post_repo.execute(count_sm)
        total = await result.scalar()

        if after_id is not None:
            rows.reverse()

        return (rows, total)
