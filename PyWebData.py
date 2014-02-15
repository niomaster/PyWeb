class PyWebData:
    def set(self, property, value):
        setattr(self, property, value)

    def get(self, property, default=None):
        if default == None or self.has(property):
            return getattr(self, property)
        else:
            self.set(property, default)
            return self.get(property)

    def has(self, property):
        return hasattr(self, property)