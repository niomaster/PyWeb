class HttpRequest:
    def __init__(self, method, path, version, headers, body = None):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers
        self.body = body

    def __str__(self):
        text = self.method + " " + "/".join(self.path) + " " + self.version + "\r\n" + "\r\n".join([ k + ": " + v for k, v in self.headers.iteritems()]) + "\r\n\r\n"
        if self.body != None:
            text += self.body
        return text