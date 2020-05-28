
"""
this is a mock dispatcher, it does nothing, just implements whatever tee needs it to implement
"""
class DBDispatcher:
    def __init__(self, db):
        self.db = db

    def start(self):
        pass

    def stop(self):
        pass

    def result_publisher(self, f, message_encoder=None):
        return lambda *args, **kwargs: f(self.db, *args, **kwargs)

    @property
    def running(self):
        return True
