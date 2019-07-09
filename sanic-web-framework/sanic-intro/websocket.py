import asyncio

from sanic import Sanic

app = Sanic()


@app.websocket('/feed')
async def feed(request, ws):
    while True:
        data = 'hello!'
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)


if __name__ == '__main__':
    # app.add_websocket_route(feed, '/feed')

    app.run()
