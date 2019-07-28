import logging
import asyncio
from datetime import datetime, time, timedelta
import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..services import StatService

logger = logging.getLogger('app')


class Schedule(object):
    def __init__(self, config, db, cache):
        self.config = config
        self.db = db
        self.cache = cache

    async def stat_user(self, user_id=None):
        stat_service = StatService(self.config, self.db, self.cache)
        if user_id is None:
            await stat_service.stat_all_users()
        else:
            user_stat = await stat_service.stat_user(user_id)
            print(user_stat)

    async def stat_post(self, post_id=None):
        stat_service = StatService(self.config, self.db, self.cache)
        if post_id is None:
            await stat_service.stat_all_posts()
        else:
            post_stat = await stat_service.stat_post(post_id)
            print(post_stat)

    def run(self, task=None, *args, **kwargs):
        if task is None:
            scheduler = AsyncIOScheduler()

            scheduler.add_job(self.stat_user, 'interval', minutes=1)
            scheduler.add_job(self.stat_post, 'interval', minutes=1)

            scheduler.start()

            try:
                asyncio.get_event_loop().run_forever()
            except (KeyboardInterrupt, SystemExit):
                pass
            except Exception as e:
                traceback.print_exc()
                logger.error(repr(e))
        else:
            method = getattr(self, task)
            asyncio.get_event_loop().run_until_complete(method(*args, **kwargs))
