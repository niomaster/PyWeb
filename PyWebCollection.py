import pickle

class PyWebCollection:
    def __init__(self, fileName = None):
        if fileName == None:
            self.storage = []
        else:
            data = open(fileName, 'rb').read()
            assert data[0:3] = "pwc", "File " + fileName + " is not a collection"
            self.storage = pickle.loads(data[3:])

    def insert(self, obj):
        self.storage.append(obj)

    def generateNeqLambda(self, condition):
        current = lambda element: True
        for key, value in condition.iteritems():
            assert key[0] != "$", "Can't nest function in $neq"
            current = lambda element: getattr(element, key) != value and current(element)
        return current

    def generateOrLambda(self, condition):
        current = lambda element: False
        for key, value in condition.iteritems():
            current = lambda element: generateLambda({ key: value })(element) or current(element)
        return current

    def generateLambda(self, condition):
        current = lambda element: True
        for key, value in condition.iteritems():
            if key[0] == "$":
                func = key[1:]
                if func == "neq":
                    current = lambda element: self.generateNeqLambda(value) and current(element)
                elif func == "or":
                    current = lambda element: self.generateOrLambda(value) and current(element)
                elif func == "lambda":
                    current = lambda element: value(element) and current(element)
            else:
                current = lambda element: getattr(element, key) == value and current(element)
        return current

    def select(self, condition):
        return filter(self.generateLambda(condition), self.storage)

    def delete(self, conidition):
        self.storage = self.select(condition)

    def update(self, condition, values):
        for element in self.select(condition):
            for key, value in values.iteritems():
                setattr(element, key, value)

    def save(self, fileName):
        f = open(fileName, "wb")
        f.write("pws")
        f.write(pickle.dumps(self.storage))
        f.close()