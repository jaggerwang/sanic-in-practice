import sqlalchemy as sa

from ..models import metadata


class Model(object):
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

        self.engine = sa.create_engine(
            'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                config['MYSQL_USER'], config['MYSQL_PASSWORD'],
                config['MYSQL_HOST'], config['MYSQL_PORT'],
                config['MYSQL_DB']))

    def create_tables(self, tables=None):
        if isinstance(tables, str):
            tables = [tables]

        metadata.create_all(self.engine, tables)
