import imp

class PyWebActionView:
    def __init__(self, python):
        self.python = python

    def render(self, data):
        module = imp.load_source("action", self.python)
        try:
            newLocation = module.invoke(data)
        except AssertionError, e:
            if type(e.message) is str:
                newLocation = e.message
            else:
                newLocation = e.message[0]
                data.session.error = e.message[1]
        
        return { "body": None, "code": 302, "message": "Found", "headers": { "Location": newLocation } }