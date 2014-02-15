from HttpRequestParseException import *
from HttpRequest import *

_Methods = [ "GET", "POST" ]

class HttpStream:
    def __init__(self, connection):
        self.connection = connection
        self.buffer = ""

    def read_char(self):
        if len(self.buffer) == 0:
            return self.connection.recv(1)[0]
        else:
            data = self.buffer[0]
            self.buffer = self.buffer[1:]
            return data

    def read(self, length):
        return "".join([ self.read_char() for i in range(length) ])

    def peek_char(self):
        if len(self.buffer) == 0:
            self.buffer = self.connection.recv(1)

        return self.buffer[0]

    def read_line(self):
        line = ""

        while self.peek_char() != "\r" and self.peek_char() != "\n":
            line += self.read_char()

        self.read_char()
        if self.peek_char() == "\r" or self.peek_char() == "\n":
            self.read_char()

        return line

    def read_request(self):
        try:
            request = self.read_line().split(" ")
            assert len(request) == 3, "Invalid request line"

            method = request[0]
            path = request[1].split("/")[1:]
            version = request[2]

            assert method in _Methods, "Unknown method " + method
            assert version == "HTTP/1.1", "Unknown HTTP version " + version

            headers = {}

            line = self.read_line()
            while line != "":
                elements = line.split(":", 1)
                assert len(elements) == 2, "Malformed header: " + line
                headers[elements[0].strip().lower()] = elements[1].strip()

                line = self.read_line()

            if method == "POST":
                if "content-length" in headers:
                    body = self.read(int(headers["content-length"]))
                    return HttpRequest(method, path, version, headers, body)
                elif "transfer-encoding" in headers and headers["transfer-encoding"] == "chunked":
                    # TODO: implement
                    assert False, "Chunked encoding not supported yet"
            else:
                return HttpRequest(method, path, version, headers)
        except AssertionError, e:
            raise HttpRequestParseException(e.message)

    def write_response(self, response):
        self.connection.send(str(response))
        self.connection.close()