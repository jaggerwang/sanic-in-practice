from aiomysql.sa import create_engine
import aioredis

from .common import metadata
from .storage import StorageRegion, FileModel, FileSchema
from .post import PostType, PostModel, PostSchema, PostLikeModel
from .user import UserModel, UserSchema


async def init_db(config):
    db = await create_engine(
        minsize=config['MYSQL_POOL_MIN_SIZE'],
        maxsize=config['MYSQL_POOL_MIN_SIZE'],
        pool_recycle=3600, host=config['MYSQL_HOST'], port=config['MYSQL_PORT'],
        user=config['MYSQL_USER'], password=config['MYSQL_PASSWORD'],
        db=config['MYSQL_DB'], echo=config['DEBUG'], charset='utf8mb4',
        connect_timeout=config['MYSQL_TIMEOUT'], autocommit=True)
    return db


async def close_db(db):
    db.close()
    await db.wait_closed()


async def init_cache(config):
    cache = await aioredis.create_redis_pool(
        config['REDIS_URI'], timeout=config['REDIS_TIMEOUT'],
        minsize=config['REDIS_POOL_MIN_SIZE'],
        maxsize=config['REDIS_POOL_MAX_SIZE'])
    return cache


async def close_cache(cache):
    cache.close()
    await cache.wait_closed()
