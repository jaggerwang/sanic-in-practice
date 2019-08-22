import os

import sqlalchemy.sql as sasql

from ..dependencies import FileRepo


class StorageService:
    def __init__(self, config: dict, file_repo: FileRepo):
        self.config = config
        self.file_repo = file_repo

    async def create_file(self, **data):
        return await self.file_repo.create(**data)

    async def modify_file(self, id, **data):
        return await self.file_repo.modify(id, **data)

    async def file_info(self, id):
        return await self.file_repo.info(id)

    async def file_infos(self, ids):
        return await self.file_repo.infos(ids)

    async def file_list(self, *, user_id=None, limit=None, offset=None):
        where = []
        if user_id is not None:
            where.append(self.file_repo.c.user_id == user_id)
        where = sasql.and_(*where) if where else None

        order_by = self.file_repo.c.id.desc()

        return await self.file_repo.list(
            where=where, order_by=order_by, limit=limit, offset=offset)
