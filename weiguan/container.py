import logging
import asyncio

from dependency_injector import providers, containers
from aiomysql.sa import create_engine, Engine
from aioredis import create_redis_pool, Redis

from .utils import SingletonMeta
from .dependencies import MessageChannel, PostRepo, PostLikeRepo, UserStatRepo, \
    PostStatRepo, FileRepo, UserRepo, UserFollowRepo
from .services import MessageService, PostService, StatService, FileService, \
    UserService
from .cli.commands import RootCommand, ModelCommand, ScheduleCommand


class _Container(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    db = providers.Configuration('db')
    cache = providers.Configuration('cache')

    app_logger = providers.Callable(logging.getLogger, name='app')

    message_channel = providers.Singleton(
        MessageChannel, config=config, cache=cache)
    post_repo = providers.Singleton(PostRepo, db=db)
    post_like_repo = providers.Singleton(PostLikeRepo, db=db)
    user_stat_repo = providers.Singleton(UserStatRepo, db=db)
    post_stat_repo = providers.Singleton(PostStatRepo, db=db)
    file_repo = providers.Singleton(FileRepo, db=db)
    user_repo = providers.Singleton(UserRepo, db=db)
    user_follow_repo = providers.Singleton(UserFollowRepo, db=db)

    message_service = providers.Singleton(
        MessageService, config=config, channel=message_channel)
    user_service = providers.Singleton(
        UserService, config=config, user_repo=user_repo,
        user_follow_repo=user_follow_repo)
    post_service = providers.Singleton(
        PostService, config=config, post_repo=post_repo,
        post_like_repo=post_like_repo, user_follow_repo=user_follow_repo)
    stat_service = providers.Singleton(
        StatService, config=config, user_stat_repo=user_stat_repo,
        post_stat_repo=post_stat_repo, user_repo=user_repo,
        user_follow_repo=user_follow_repo, post_repo=post_repo,
        post_like_repo=post_like_repo)
    file_service = providers.Singleton(
        FileService, config=config, file_repo=file_repo)

    model_command = providers.Factory(ModelCommand, config=config)
    schedule_command = providers.Factory(
        ScheduleCommand, config=config, logger=app_logger,
        stat_service=stat_service)
    root_command = providers.Factory(
        RootCommand, model=model_command, schedule=schedule_command)


class Container(metaclass=SingletonMeta):
    def __init__(self, config: dict = None, log_config: dict = None):
        self.on_init = asyncio.create_task(self._init(config, log_config))

    async def _init(self, config: dict, log_config: dict):
        logging.config.dictConfig(log_config)

        db: Engine = await create_engine(
            minsize=config['MYSQL_POOL_MIN_SIZE'],
            maxsize=config['MYSQL_POOL_MIN_SIZE'],
            pool_recycle=3600, host=config['MYSQL_HOST'],
            port=config['MYSQL_PORT'], user=config['MYSQL_USER'],
            password=str(config['MYSQL_PASSWORD']),
            db=config['MYSQL_DB'], echo=config['DEBUG'],
            charset='utf8mb4', connect_timeout=config['MYSQL_TIMEOUT'],
            autocommit=True)

        cache: Redis = await create_redis_pool(
            config['REDIS_URI'], timeout=config['REDIS_TIMEOUT'],
            minsize=config['REDIS_POOL_MIN_SIZE'],
            maxsize=config['REDIS_POOL_MAX_SIZE'])

        self.container = _Container(config=config, db=db, cache=cache)

        await self.message_channel.on_init

    async def clean(self):
        self.db.close()
        await self.db.wait_closed()

        self.cache.close()
        await self.cache.wait_closed()

    @property
    def config(self) -> dict:
        return self.container.config()

    @property
    def db(self) -> Engine:
        return self.container.db()

    @property
    def cache(self) -> Redis:
        return self.container.cache()

    @property
    def app_logger(self) -> logging.Logger:
        return self.container.app_logger()

    @property
    def message_channel(self) -> MessageChannel:
        return self.container.message_channel()

    @property
    def post_repo(self) -> PostRepo:
        return self.container.post_repo()

    @property
    def post_like_repo(self) -> PostLikeRepo:
        return self.container.post_like_repo()

    @property
    def user_stat_repo(self) -> UserStatRepo:
        return self.container.user_stat_repo()

    @property
    def post_stat_repo(self) -> PostStatRepo:
        return self.container.post_stat_repo()

    @property
    def file_repo(self) -> FileRepo:
        return self.container.file_repo()

    @property
    def user_repo(self) -> UserRepo:
        return self.container.user_repo()

    @property
    def user_follow_repo(self) -> UserFollowRepo:
        return self.container.user_follow_repo()

    @property
    def message_service(self) -> MessageService:
        return self.container.message_service()

    @property
    def user_service(self) -> UserService:
        return self.container.user_service()

    @property
    def post_service(self) -> PostService:
        return self.container.post_service()

    @property
    def stat_service(self) -> StatService:
        return self.container.stat_service()

    @property
    def file_service(self) -> FileService:
        return self.container.file_service()

    @property
    def model_command(self) -> ModelCommand:
        return self.container.model_command()

    @property
    def schedule_command(self) -> ScheduleCommand:
        return self.container.schedule_command()

    @property
    def root_command(self) -> RootCommand:
        return self.container.root_command()
