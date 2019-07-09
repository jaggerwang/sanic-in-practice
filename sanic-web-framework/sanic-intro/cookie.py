from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.get("/read")
def read(request):
    return json({
        "cookies": request.cookies,
        "SID": request.cookies.get('SID'),
    })


@app.get("/write")
def write(request):
    response = json({})

    response.cookies['SID'] = 'rfBk1o3UIH4S6JXuc1Qv8j0iM586ACZg'
    response.cookies['SID']['max-age'] = 3600

    return response


@app.get("/delete")
def delete(request):
    response = json({})

    del response.cookies['SID']

    return response


if __name__ == '__main__':
    app.run()
