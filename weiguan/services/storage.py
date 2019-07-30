import os

import sqlalchemy.sql as sasql

from ..models import FileModel


class StorageService:
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    async def create_file(self, **data):
        async with self.db.acquire() as conn:
            result = await conn.execute(sasql.insert(FileModel).values(**data))
            id = result.lastrowid

        return await self.file_info(id)

    async def edit_file(self, id, **data):
        data = {k: v for k, v in data.items() if v is not None}

        async with self.db.acquire() as conn:
            await conn.execute(
                sasql.update(FileModel).where(FileModel.c.id == id).
                values(**data))

        return await self.file_info(id)

    async def file_info(self, id):
        if id is None:
            return None

        async with self.db.acquire() as conn:
            result = await conn.execute(
                FileModel.select().where(FileModel.c.id == id))
            row = await result.first()

        return None if row is None else dict(row)

    async def file_infos(self, ids):
        valid_ids = [v for v in ids if v is not None]
        if valid_ids:
            async with self.db.acquire() as conn:
                result = await conn.execute(
                    FileModel.select().where(FileModel.c.id.in_(valid_ids)))
                d = {v['id']: dict(v) for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v) for v in ids]

    async def file_list(self, *, user_id=None, limit=None, offset=None):
        select_sm = FileModel.select()
        count_sm = sasql.select([sasql.func.count()]).\
            select_from(FileModel)

        if user_id is not None:
            clause = FileModel.c.user_id == user_id
            select_sm = select_sm.where(clause)
            count_sm = count_sm.where(clause)

        select_sm = select_sm.order_by(FileModel.c.id.desc())

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
