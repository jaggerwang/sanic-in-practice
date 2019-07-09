from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.get("/query")
def query(request):
    return json({
        "query": request.query_string,
        "args": request.args,
        "args_with_blank": request.get_args(keep_blank_values=True),
        "query_args": request.query_args,
        "query_args_with_blank": request.get_query_args(keep_blank_values=True),
    })


@app.post('/files')
def files(request):
    return json({
        'files': request.files,
        'file': request.files.get('file'),
        'file_list': request.files.getlist('file'),
        'file_dict': {
            'name': request.files.get('file').name,
            'type': request.files.get('file').type,
            'body': request.files.get('file').body,
        },
    })


@app.post('/form')
def form(request):
    return json({
        'form': request.form,
        'name': request.form.get('name'),
        'name_list': request.form.getlist('name'),
    })


@app.get('/headers')
def headers(request):
    return json({
        'headers': request.headers,
        'token': request.headers.get('X-Token'),
        'token_list': request.headers.getall('X-Token', []),
    })


if __name__ == '__main__':
    app.run()
