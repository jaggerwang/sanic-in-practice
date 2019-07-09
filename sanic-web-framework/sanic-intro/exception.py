from sanic import Sanic
from sanic.response import text
from sanic.exceptions import NotFound, ServerError

app = Sanic()


@app.route('/')
def index(request):
    return text('Index')


@app.route('/error')
def error(request):
    raise ServerError('Internal server error')


@app.exception(NotFound)
def default_page(request, exception):
    return text("Default page: {}".format(request.url))


def server_error_handler(request, exception):
    return text("Oops, server error", status=500)


if __name__ == '__main__':
    app.error_handler.add(Exception, server_error_handler)

    app.run()
