import os

import sqlalchemy.sql as sasql

from ..adapter.repository import FileRepo
from ..usecase import NotFoundException


class FileUsecase:
    def __init__(self, config: dict, file_repo: FileRepo):
        self.config = config
        self.file_repo = file_repo

    async def create(self, **data):
        return await self.file_repo.create(**data)

    async def info(self, id):
        if id is None:
            return None

        file = await self.file_repo.info(id)
        if file is None:
            raise NotFoundException('文件未找到')

        return file

    async def infos(self, ids):
        return await self.file_repo.infos(ids)
