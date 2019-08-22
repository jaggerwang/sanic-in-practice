import asyncio

import fire
import uvloop

from ..config import config, log_config
from ..container import Container


async def init_container():
    container = Container(config, log_config)
    await container.on_init

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_container())

    container = Container()
    fire.Fire(container.root_command)

    loop.run_until_complete(container.clean())
