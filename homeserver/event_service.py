class EventMessage():

    def __init__(self, msg, origin):
        self.msg = msg
        self.origin = origin
    
    def __repr__(self):
        return "{}: {} from source: {}.".format(self.__class__.__name__, self.msg, self.origin)
