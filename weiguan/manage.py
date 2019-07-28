import logging
import asyncio

import fire

from .config import config, get_log_config
from .models import init_db, init_cache
from .commands import Model, Schedule


class Manage(object):
    def __init__(self, config):
        self.config = config

    async def init(self):
        self.db = await init_db(self.config)
        self.cache = await init_cache(self.config)

        self.model = Model(self.config, self.db, self.cache)
        self.schedule = Schedule(self.config, self.db, self.cache)


if __name__ == '__main__':
    logging.config.dictConfig(get_log_config(config))

    manage = Manage(config)
    asyncio.get_event_loop().run_until_complete(manage.init())

    fire.Fire(manage)
