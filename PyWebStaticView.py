import os

_MimeTypes = { "html": "text/html; charset=utf-8", "htm": "text/html; charset=utf-8", "js": "text/javascript",
    "png": "image/png", "jpg": "image/jpeg" }

_DefaultMimeType = "application/octet-stream"

class PyWebStaticView:
    def __init__(self, path):
        self.file = path
        extension = os.path.splitext(path)[1][1:]

        if extension in _MimeTypes:
            self.mimetype = _MimeTypes[extension]
        else:
            self.mimetype = _DefaultMimeType

    def render(self, data):
        return { "body": open(self.file, "rb").read(), "contentType": self.mimetype }