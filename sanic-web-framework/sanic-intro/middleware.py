from sanic import Sanic
from sanic.response import text

app = Sanic()


@app.route('/')
def index(request):
    return text('Index: {}'.format(request['foo']))


@app.middleware('request')
async def print_on_request(request):
    print("I print when a request is received by the server")


@app.middleware('response')
async def print_on_response(request, response):
    print("I print when a response is returned by the server")


@app.middleware('request')
async def add_key(request):
    request['foo'] = 'bar'


@app.middleware('response')
async def custom_banner(request, response):
    response.headers["Server"] = "Fake-Server"


# @app.middleware('request')
async def halt_request(request):
    return text('I halted the request')


# @app.middleware('response')
async def halt_response(request, response):
    return text('I halted the response')

if __name__ == '__main__':
    app.run()
