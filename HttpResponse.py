class HttpResponse:
    def __init__(self, body="", code=200, message="OK", contentType="text/html; charset=UTF-8", version="HTTP/1.1", headers={}):
        if body != None:
            # TODO: encoding?
            headers["Content-Length"] = str(len(body))
            headers["Content-Type"] = contentType

        self.body = body
        self.code = code
        self.message = message
        self.version = version
        self.headers = headers

    def __repr__(self):
        text = self.version + " " + str(self.code) + " " + self.message + "\r\n" + "\r\n".join([ k + ": " + v for k, v in self.headers.iteritems() ]) + "\r\n\r\n"
        if self.body != None:
            return text + self.body
        else:
            return text