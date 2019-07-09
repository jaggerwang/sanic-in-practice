from sanic import Sanic
from sanic import response

app = Sanic()


@app.route('/text')
def text(request):
    return response.text('Hello world!')


@app.route('/html')
def html(request):
    return response.html('<p>Hello world!</p>')


@app.route('/json')
def json(request):
    return response.json({'message': 'Hello world!'})


@app.route('/file')
async def file(request):
    return await response.file('/tmp/file.txt')


@app.route('/redirect')
def redirect(request):
    return response.redirect('/json')


@app.route('/raw')
def raw(request):
    return response.raw(b'raw data')


@app.route('/status')
def status(request):
    return response.json(
        {'message': 'Hello world!'},
        headers={'X-Served-By': 'sanic'},
        status=200
    )


if __name__ == '__main__':
    app.run()
