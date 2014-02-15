import socket
from HttpClientHandler import *
from HttpResponse import *

_DefaultBody = """<!doctype html>
<html>
    <head>
        <title>HTTP Server Running</title>
    </head>
    <body>
        <h1>It works!</h1>
        Now add a handler for get requests and start coding!
    </body>
</html>"""

_Default404 = """<!doctype html>
<html>
    <head>
        <title>404 Not Found</title>
        <body>
            <h1>404 - Not Found</h1>
            The requested document was not found
        </body>
    </head>
</html>"""

class HttpServer:
    maxPostSize = 1048576

    def __init__(self, bindAddress):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(bindAddress)

    def get_response(self, request):
        if request.method == "GET":
            return self.get(request.path, request.headers)
        elif request.method == "POST":
            return self.post(request.path, request.headers, request.body)

    def get(self, path, headers):
        if path == [""]:
            return HttpResponse(body=_DefaultBody)
        else:
            return HttpResponse(body=_Default404, code=404, message="Not Found")

    def post(self, path, headers):
        return self.get(path)

    def serve_forever(self):
        # self.socket.settimeout(0.1)
        self.socket.listen(1)
        while True:
            try:
                connection, address = self.socket.accept()
                handler = HttpClientHandler(connection, self)
                handler.start()
            except socket.timeout:
                pass

    def serve_one(self):
        self.socket.listen(1)
        connection, address = self.socket.accept()
        handler = HttpClientHandler(connection, self)
        handler.start()

if __name__ == "__main__":
    server = HttpServer(("0.0.0.0", 80))
    server.serve_forever()