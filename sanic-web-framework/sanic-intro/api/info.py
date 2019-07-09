from sanic import Blueprint
from sanic.response import text

info = Blueprint('info', url_prefix='/info')


@info.route('/')
def index(request):
    return text('Info index')
