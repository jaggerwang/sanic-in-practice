from sanic import Sanic, Blueprint
from sanic.response import json

from api import api

bp = Blueprint('bp', url_prefix='/bp')


@bp.route('/')
def bp_index(request):
    return json({'my': 'blueprint'})


if __name__ == '__main__':
    app = Sanic()

    app.blueprint(bp)
    app.blueprint(api)

    app.run()
