import os

from sanic import Sanic
from sanic_session import Session, AIORedisSessionInterface

from ..config import config, log_config
from ..container import Container
from .blueprints import handle_exception, message, post, file, user

os.makedirs(config['DATA_PATH'], 0o755, True)

app = Sanic(config['NAME'].capitalize(), log_config=log_config)
app.config.update(config)

app.error_handler.add(Exception, handle_exception)

app.static('/files', os.path.join(config['DATA_PATH'], config['UPLOAD_DIR']),
           stream_large_files=True)

app.blueprint(message)
app.blueprint(post)
app.blueprint(file)
app.blueprint(user)


@app.listener('before_server_start')
async def server_init(app, loop):
    container = Container(config, log_config)
    await container.on_init

    Session(app, AIORedisSessionInterface(
        container.cache, expiry=config['SESSION_EXPIRY']))


@app.listener('after_server_stop')
async def server_clean(app, loop):
    await Container().clean()

if __name__ == '__main__':
    app.run(host=config['HOST'], port=config['PORT'], debug=config['DEBUG'],
            auto_reload=config['AUTO_RELOAD'], access_log=config['ACCESS_LOG'],
            workers=config['WORKERS'])
