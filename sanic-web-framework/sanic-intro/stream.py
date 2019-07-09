import asyncio

from sanic import Sanic
from sanic.response import stream, file_stream

app = Sanic()


@app.post('/stream', stream=True)
async def stream_handler(request):
    async def streaming(response):
        while True:
            body = await request.stream.read()
            if body is None:
                break
            body = body.decode('utf-8').replace('1', 'A')
            await response.write(body)
    return stream(streaming)


@app.route('/file')
async def file_handler(request):
    return await file_stream('./file.txt')


if __name__ == '__main__':
    app.run()
