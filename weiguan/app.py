from sanic import Sanic
from sanic_session import Session, AIORedisSessionInterface

from .config import config, log_config
from .models import init_db, close_db, init_cache, close_cache
from .blueprints import account

app = Sanic(config['NAME'].capitalize(), log_config=log_config)
app.config.update(config)

app.blueprint(account)


@app.listener('before_server_start')
async def server_init(app, loop):
    app.db = await init_db(config)

    app.cache = await init_cache(config)

    Session(app, AIORedisSessionInterface(
        app.cache, expiry=config['SESSION_EXPIRY']))


@app.listener('after_server_stop')
async def server_clean(app, loop):
    await close_cache(app.cache)

    await close_db(app.db)

if __name__ == '__main__':
    app.run(host=config['HOST'], port=config['PORT'], debug=config['DEBUG'],
            auto_reload=config['AUTO_RELOAD'], access_log=config['ACCESS_LOG'],
            workers=config['WORKERS'])
