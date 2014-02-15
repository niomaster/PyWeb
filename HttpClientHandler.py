import threading
from HttpStream import *
from HttpRequestParseException import *

class HttpClientHandler(threading.Thread):
    def __init__(self, connection, server):
        threading.Thread.__init__(self)
        # connection.settimeout(0)
        self.stream = HttpStream(connection)
        self.server = server

    def run(self):
        try:
            request = self.stream.read_request()
            print request.method, "/" + "/".join(request.path), request.version, "->",
            response = self.server.get_response(request)
            print response.version, response.code, response.message
            self.stream.write_response(response)
        except HttpRequestParseException, e:
            print "Parse exception: " + e.message