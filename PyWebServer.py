import sys
import os
import binascii
import re
from HttpServer import *
from HttpResponse import *
from PyWebView import *
from PyWebStaticView import *
from PyWebActionView import *
from PyWebData  import *

def urldecode(data):
    while data.find("%") != -1:
        position = data.find("%")
        data = data[:position] + chr(int(data[position+1:position+3], 16)) + data[position+3:]

    return data

def parseQuery(query):
    if not "=" in query:
        return {}
    dictQuery = {}
    for argument in query.split("&"):
        key, value = argument.split("=")
        dictQuery[urldecode(key)] = urldecode(value)
    return dictQuery

def parseCookies(cookieString):
    cookies = {}
    pairs = [ value.strip().split('=') for value in cookieString.split(';') ]
    for pair in pairs:
        cookies[pair[0]] = pair[1]
    return cookies

def nonce():
    return binascii.hexlify(os.urandom(64))

class PyWebServer(HttpServer):
    bindAddress = ("0.0.0.0", 80)
    sessions = {}

    def __init__(self, location):
        HttpServer.__init__(self, self.bindAddress)
        self.location = location
        self.views = {}
        self.load_views()
        self.load_static_files()
        self.load_actions()

        self.storage = PyWebData()

    def get_name(self, root, location):
        return location[len(root)+len(os.path.sep):]

    def load_views(self):
        viewLocation = os.path.join(self.location, "views")

        for root, dirs, files in os.walk(viewLocation):
            for filename in files:
                if filename[-5:] == ".html":
                    self.load_view(viewLocation, os.path.join(root, os.path.splitext(filename)[0]))

        print len(self.views), "views loaded"

    def load_view(self, root, location):
        if os.path.exists(location + ".py") and os.path.exists(location + ".html"):
            name = self.get_name(root, location)
            self.views[name] = PyWebView(location)

    def load_static_files(self):
        staticLocation = os.path.join(self.location, "static")

        static = 0

        for root, dirs, files in os.walk(staticLocation):
            for filename in files:
                if filename[-5:] == ".html":
                    name = self.get_name(staticLocation, os.path.join(root, os.path.splitext(filename)[0]))
                else:
                    name = self.get_name(staticLocation, os.path.join(root, filename))
                self.views[name] = PyWebStaticView(os.path.join(root, filename))
                static += 1

        print static, "static files loaded"

    def load_actions(self):
        actionLocation = os.path.join(self.location, "actions")

        actions = 0

        for root, dirs, files in os.walk(actionLocation):
            for filename in files:
                if filename[-3:] == ".py":
                    name = self.get_name(actionLocation, os.path.join(root, os.path.splitext(filename)[0]))
                    self.views[name] = PyWebActionView(os.path.join(root, filename))
                    actions += 1

        print actions, "actions loaded"

    def get(self, path, headers):
        return self.respond(path, headers)

    def post(self, path, headers, post):
        return self.respond(path, headers, post)

    def respond(self, path, headers, post = None):
        if "cookie" in headers:
            cookies = parseCookies(headers["cookie"])
            if "session" in cookies and cookies["session"] in self.sessions:
                sessionId = cookies["session"]
                session = self.sessions[sessionId]
            else:
                sessionId = nonce()
                session = self.sessions[sessionId] = PyWebData()
        else:
            sessionId = nonce()
            session = self.sessions[sessionId] = PyWebData()

        if path[-1] == "":
            path[-1] = "index"
            query = ""
        else:
            if "?" in path[-1]:
                query = path[-1].split("?")[1].split("#")[0]
            else:
                query = ""
            path[-1] = path[-1].split("?")[0].split("#")[0]

        view = os.path.join(*path)
        
        data = PyWebData()
        data.session = session
        data.http = PyWebData()
        data.http.post = post
        data.http.query = parseQuery(query)
        data.http.headers = headers
        data.storage = self.storage

        if data.http.post != None and "content-type" in data.http.headers:
            if data.http.headers["content-type"].split(";")[0].strip().lower() == "application/x-www-form-urlencoded":
                data.http.post = parseQuery(data.http.post)

        try:
            if view in self.views:
                args = self.views[view].render(data)
            elif "404" in self.views:
                args = self.views["404"].render(data)
                args["code"] = 404
                args["message"] = "Not Found"
            else:
                # TODO: Default 404
                args = { "body": "", "code": 404, "message": "Not Found" }

            if not "headers" in args:
                args["headers"] = {}

            args["headers"]["Set-Cookie"] = "session="+sessionId

            return HttpResponse(**args)

        except PyWebViewException, e:

            return HttpResponse("<html><head><title>Internal Server Error</title></head><body><h1>Error message</h1>An error occured while loading this view: " + e.message + "</body></html>", 500, "Internal Server Error")

    def serve_forever(self):
        if "__init__" in self.views:
            data = PyWebData()
            data.storage = self.storage
            self.views["__init__"].render(data)
            print "Initialization called"

        print "Now serving on", self.bindAddress[0] + ":" + str(self.bindAddress[1])
        try:
            HttpServer.serve_forever(self)
        except KeyboardInterrupt:
            print "Shutting down"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        location = os.path.abspath("test")
    else:
        location = os.path.abspath(sys.argv[1])

    server = PyWebServer(location)
    server.serve_forever()