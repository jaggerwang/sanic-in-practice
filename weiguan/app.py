import os

from sanic import Sanic
from sanic_session import Session, AIORedisSessionInterface

from .config import config, log_config
from .models import init_db, close_db, init_cache, close_cache
from .services import MessageService
from .blueprints import handle_exception, account, message, post, storage, user

os.makedirs(config['DATA_PATH'], 0o755, True)

app = Sanic(config['NAME'].capitalize(), log_config=log_config)
app.config.update(config)

app.error_handler.add(Exception, handle_exception)

app.static('/files', os.path.join(config['DATA_PATH'], config['UPLOAD_DIR']),
           stream_large_files=True)

app.blueprint(account)
app.blueprint(message)
app.blueprint(post)
app.blueprint(storage)
app.blueprint(user)


@app.listener('before_server_start')
async def server_init(app, loop):
    app.db = await init_db(config)

    app.cache = await init_cache(config)

    Session(app, AIORedisSessionInterface(
        app.cache, expiry=config['SESSION_EXPIRY']))

    app.message_service = MessageService(config, app.db, app.cache)
    await app.message_service.init()


@app.listener('after_server_stop')
async def server_clean(app, loop):
    await close_cache(app.cache)

    await close_db(app.db)

if __name__ == '__main__':
    app.run(host=config['HOST'], port=config['PORT'], debug=config['DEBUG'],
            auto_reload=config['AUTO_RELOAD'], access_log=config['ACCESS_LOG'],
            workers=config['WORKERS'])
