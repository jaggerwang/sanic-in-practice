from sanic import Blueprint
from sanic.response import text

static = Blueprint('static', url_prefix='/static')


@static.route('/')
def index(request):
    return text('Static index')
