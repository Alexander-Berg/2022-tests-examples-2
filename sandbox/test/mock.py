class MockContext(object):

    @classmethod
    def save(cls):
        pass


class MockTask(object):

    def __init__(self):
        self.Context = MockContext()
