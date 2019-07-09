from sanic import Sanic, Blueprint
from sanic.response import json, text

app = Sanic()


@app.route('/hello', version=1)
def hello(request):
    return text('Hello world! Version 1')


@app.route('/hello', version=2)
def hello(request):
    return text('Hello world! Version 2')


bp = Blueprint('bp', url_prefix='/bp', version=1)


@bp.route('/')
def bp_index(request):
    return json({'my': 'blueprint'})


if __name__ == '__main__':
    app.blueprint(bp)

    app.run()
