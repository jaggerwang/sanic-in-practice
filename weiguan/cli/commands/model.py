import sqlalchemy as sa

from ...adapter.repository import metadata


class ModelCommand:
    def __init__(self, config: dict):
        self.config = config

        self.engine = sa.create_engine(
            'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                config['MYSQL_USER'], config['MYSQL_PASSWORD'],
                config['MYSQL_HOST'], config['MYSQL_PORT'],
                config['MYSQL_DB']))

    def create_tables(self, tables=None):
        if isinstance(tables, str):
            tables = [tables]

        metadata.create_all(self.engine, tables)
