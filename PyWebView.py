import imp
from PyWebViewStructure import *

class PyWebView:
    def __init__(self, location):
        self.python = location + ".py"
        self.html = location + ".html"

    def render(self, data):
        module = imp.load_source("view", self.python)
        structure = PyWebViewStructure(open(self.html).read())
        return { "body": structure.toHtml(module, data) }