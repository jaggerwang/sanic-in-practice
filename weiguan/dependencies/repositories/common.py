import sqlalchemy as sa
import sqlalchemy.sql as sasql
from aiomysql.sa import Engine, SAConnection

metadata = sa.MetaData()


class Repository:
    def __init__(self, db: Engine, table: sa.Table):
        self.db = db
        self.table = table

    @property
    def conn(self):
        return self.db.acquire()

    async def execute(self, sm):
        conn: SAConnection
        async with self.conn as conn:
            result = await conn.execute(sm)

        return result

    async def create(self, **data):
        result = await self.execute(sasql.insert(self.table).values(**data))
        id = result.lastrowid

        return await self.info(id)

    async def delete(self, column_value, column_name='id'):
        result = await self.execute(
            sasql.delete(self.table)
            .where(self.table.c[column_name] == column_value))

        return result.rowcount

    async def modify(self, column_value, column_name='id', **data):
        data = {k: v for k, v in data.items() if v is not None}

        await self.execute(
            sasql.update(self.table)
            .where(self.table.c[column_name] == column_value)
            .values(**data))

        return await self.info(column_value, column_name)

    async def info(self, column_value, column_name='id'):
        if column_value is None:
            return None

        result = await self.execute(
            self.table.select()
            .where(self.table.c[column_name] == column_value))
        row = await result.first()

        return None if row is None else dict(row)

    async def infos(self, column_values, column_name='id'):
        valid_values = [v for v in column_values if v is not None]
        if valid_values:
            result = await self.execute(
                self.table.select()
                .where(self.table.c[column_name].in_(valid_values)))
            d = {v[column_name]: dict(v) for v in await result.fetchall()}
        else:
            d = {}

        return [d.get(v) for v in column_values]

    async def list(self, *, from_=None, where=None, order_by=None, limit=None,
                   offset=None):
        select_sm = self.table.select()
        count_sm = sasql.select([sasql.func.count()]).select_from(self.table)

        if from_ is not None:
            select_sm = select_sm.select_from(from_)
            count_sm = count_sm.select_from(from_)

        if where is not None:
            select_sm = select_sm.where(where)
            count_sm = count_sm.where(where)

        if order_by is not None:
            select_sm = select_sm.order_by(order_by)

        if limit is not None:
            select_sm = select_sm.limit(limit)
        if offset is not None:
            select_sm = select_sm.offset(offset)

        result = await self.execute(select_sm)
        rows = [dict(v) for v in await result.fetchall()]

        result = await self.execute(count_sm)
        total = await result.scalar()

        return (rows, total)

    async def count(self, where=None):
        sm = sasql.select([sasql.func.count()]).select_from(self.table)
        if where is not None:
            sm = sm.where(where)
        result = await self.execute(sm)

        return await result.scalar()
