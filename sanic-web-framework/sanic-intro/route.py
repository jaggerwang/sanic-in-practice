from sanic import Sanic
from sanic.response import text, redirect

app = Sanic()


@app.route('/tag/<tag>')
def tag_handler(request, tag):
    return text('Tag - {}'.format(tag))


@app.route('/integer/<integer:int>')
def integer_handler(request, integer):
    return text('Integer - {}'.format(integer))


@app.route('/number/<number:number>')
def number_handler(request, number):
    return text('Number - {}'.format(number))


@app.route('/person/<name:[A-z]+>')
def person_handler(request, name):
    return text('Person - {}'.format(name))


def folder_handler(request, folder):
    return text('Folder - {}'.format(folder))


@app.route('/get', methods=['GET'])
def get_handler(request):
    return text('GET request - {}'.format(request.args))


@app.post('/post')
def post_handler(request):
    return text('POST request - {}'.format(request.args))


@app.route('/host', host='jaggerwang.net')
def host_jaggerwang_net_handler(request):
    return text('GET request in jaggerwang.net - {}'.format(request.args))


@app.route('/host')
def host_default_handler(request):
    return text('GET request in default - {}'.format(request.args))


@app.route('/')
def index(request):
    url = app.url_for('posts_handler', post_id=5,
                      limit=10, offset=10, status=[1, 2])
    return redirect(url)


@app.route('/posts/<post_id:int>')
def posts_handler(request, post_id):
    return text('Post - {}'.format(post_id))


@app.route('/url')
def url_handler(request):
    return text('{}\n{}\n{}\n{}'.format(
        app.url_for('static', filename='test.css'),
        app.url_for('static', filename='test.css', name='static'),
        app.url_for('static', filename='test.txt', name='uploads'),
        app.url_for('static', name='the_file'),
    ))


if __name__ == '__main__':
    app.add_route(folder_handler, '/folder/<folder:[A-z0-9]{0,4}>')

    app.static('/static', './static')
    app.static('/uploads', './uploads', name='uploads')
    app.static('/the_file.txt', './file.txt', name='the_file')

    app.run()
