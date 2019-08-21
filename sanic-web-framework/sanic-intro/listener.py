import asyncio

from sanic import Sanic
from sanic.response import text

app = Sanic()


@app.route('/')
def index(request):
    return text('Index: {}'.format(request['foo']))


@app.listener('before_server_start')
async def setup_db(app, loop):
    app.db = {'host': 'localhost', 'port': 3306}


@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('Server successfully started!')


@app.listener('before_server_stop')
async def notify_server_stopping(app, loop):
    print('Server shutting down!')


@app.listener('after_server_stop')
async def close_db(app, loop):
    app.db = None


async def start_monitor():
    await asyncio.sleep(5)
    print('Monitor started!')

if __name__ == '__main__':
    app.add_task(start_monitor())

    app.run()
