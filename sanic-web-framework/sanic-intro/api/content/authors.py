from sanic import Blueprint
from sanic.response import text

authors = Blueprint('authors', url_prefix='/authors')


@authors.route('/')
def index(request):
    return text('Authors index')
