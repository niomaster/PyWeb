import re
import traceback
from PyWebViewException import *
_TemplateRegex = re.compile("""<[\s]*template[\s]+name[\s]*=[\s]*['"]{0,1}([^'"\s>]*)['"]{0,1}[\s]*>(.*?)<[\s]*/[\s]*template[\s]*>""", re.DOTALL)
_BodyRegex = re.compile("""<[\s]*body[\s]*>(.*?)<[\s]*/[\s]*body[\s]*>""", re.DOTALL)
_HeadRegex = re.compile("""<[\s]*head[\s]*>(.*?)<[\s]*/[\s]*head[\s]*>""", re.DOTALL)

_Whitespace = re.compile("[\s]")
_ControlRegex = re.compile("""({[^}]*})""")

_StackUp = [ "forall" ]
_StackDown = [ "/forall" ]

class PyWebViewStructureData:
    def __init__(self, context, data):
        self.context = context
        self.data = data

    def run(self, structure, module, data):
        return self.data

class PyWebViewStructureTemplate:
    def __init__(self, context, name, data = None):
        self.context = context
        self.templateName = name
        self.data = data

    def run(self, structure, module, data):
        assert self.templateName in structure.templates, "Template " + self.templateName + " doesn't exist in context" + self.context

        if data == None:
            data = structure.genericData(self.templateName, module)

        if data != None:
            if self.data != None:
                data = structure.getattr(self.data, data)

            return structure.runCode(structure.templates[self.templateName], module, data)
        else:
            return structure.runCode(structure.templates[self.templateName], module, None)

class PyWebViewStructurePrintMember:
    def __init__(self, context, member = None):
        self.context = context
        self.member = member

    def run(self, structure, module, data):
        assert data != None, "Can't retrieve member " + self.member + ", because the template got no data in context" + self.context
        if self.member == None:
            return data
        else:
            return structure.getattr(self.member, data)

class PyWebViewStructureForall:
    def __init__(self, context, innerCode, data = None):
        self.context = context
        self.innerCode = innerCode
        self.data = data

    def run(self, structure, module, data):
        if self.data != None:
            data = structure.getattr(self.data, data)

        assert type(data) is list, "Forall didn't get a list in context " + self.context

        return "".join([ structure.runCode(self.innerCode, module, dataElement) for dataElement in data ])

class PyWebViewStructure:
    def __init__(self, data):
        self.data = data
        self.templates = {}
        self.parse()

    def parseCode(self, context, data):
        try:
            code = []

            matches = _ControlRegex.finditer(data)
            controls = [(None, 0, None)] + [(match.start(0), match.end(0), match.group(0)[1:-1]) for match in matches]
            calls = [None] + [ filter(lambda x: x != "", _Whitespace.split(controls[i][2])) for i in range(1, len(controls)) ]
            i = 1
            while i < len(controls):
                code.append(PyWebViewStructureData(context, data[controls[i-1][1] : controls[i][0]]))

                call = calls[i]

                if call[0] == "show":
                    assert len(call) in [1, 2, 3, 5]
                    if len(call) == 1:
                        code.append(PyWebViewStructurePrintMember(context))
                    elif len(call) == 2:
                        code.append(PyWebViewStructurePrintMember(context, call[1]))
                    else:
                        assert call[1] == "a" or call[1] == "an"
                        if len(call) == 3:
                            code.append(PyWebViewStructureTemplate(context, call[2]))
                        else:
                            assert call[3] == "with"
                            code.append(PyWebViewStructureTemplate(context, call[2], call[4]))
                    i += 1
                elif call[0] == "forall":
                    assert len(call) == 1 or len(call) == 2
                    stack = 1
                    start = i
                    i += 1
                    while stack != 0 and i < len(calls):
                        if calls[i][0] in _StackUp:
                            stack += 1
                        elif calls[i][0] in _StackDown:
                            stack -= 1
                        i += 1
                    assert stack == 0, "Unmatched forall control in context " + context
                    i -= 1
                    assert calls[i][0] == "/forall", "Unmatched forall control in context " + context

                    # TODO: Remove recursive re-parsing of data: this is O(n^2) at worst when foralls contain eachother.
                    innerCode = self.parseCode(context + ".forall[" + str(start) + "]", data[controls[start][1]:controls[i][0]])

                    if len(call) == 1:
                        code.append(PyWebViewStructureForall(context, innerCode))
                    else:
                        code.append(PyWebViewStructureForall(context, innerCode, call[1]))

                    i += 1
                else:
                    raise PyWebViewException("Unknown control " + call[0] + " in context " + context)

            code.append(PyWebViewStructureData(context, data[controls[-1][1]:]))

            return code
        except AssertionError, e:
            raise PyWebViewException(e.message)

    def runCode(self, code, module, data):
        stringData = ""
        for i, element in enumerate(code):
            newData = element.run(self, module, data)
            if type(newData) != str:
                raise PyWebViewException("Can't print " + str(newData) + " in context " + element.context)
            stringData += newData
        return stringData

    def genericData(self, name, module):
        if hasattr(module, "get_" + name + "_data"):
            return getattr(module, "get_" + name + "_data")(self.sessionData)
        else:
            return None

    def getattr(self, attr, data):
        attrs = attr.split(".")

        for attr in attrs:
            if type(data) is dict:
                data = data[attr]
            else:
                data = getattr(data, attr)

        return data

    def parse(self):
        templates = [ match.groups() for match in _TemplateRegex.finditer(self.data) ]
        for name, data in templates:
            if name in self.templates:
                raise PyWebViewException("Duplicate template " + name)
            else:
                self.templates[name] = self.parseCode("template[" + name + "]", data)

        body = _BodyRegex.findall(self.data)
        head = _HeadRegex.findall(self.data)

        if len(body) != 1:
            raise PyWebViewException("Wrong number of body tags")
        if len(head) != 1:
            raise PyWebViewException("Wrong number of head tags")

        self.body = self.parseCode("body", body[0])
        self.head = self.parseCode("head", head[0])

    def toHtml(self, module, data):
        self.sessionData = data
        try:
            html  = "<!doctype html><html><head>"
            html += self.runCode(self.head, module, self.genericData("head", module))
            html += "</head><body>"
            html += self.runCode(self.body, module, self.genericData("body", module))
            html += "</body></html>"
            return html
        except AssertionError, e:
            raise PyWebViewException(e.message)
        except Exception, e:
            raise PyWebViewException("<pre>" + traceback.format_exc() + "</pre>")