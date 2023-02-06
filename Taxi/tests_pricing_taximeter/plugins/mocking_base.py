def check_called(mocks, times=None):
    if times is not None and times == 0:
        assert not mocks.has_calls
    else:
        assert mocks.has_calls
        if times:
            assert mocks.times_called == times


def check_called_once(mocks):
    check_called(mocks, 1)


def check_not_called(mocks):
    check_called(mocks, 0)


class BasicMock:
    """Class provides basic error processing for mock"""

    def __init__(self):
        self.timeout = False
        self.internal = False
        self.response = None
        self.content_type = None

    def must_timeout(self):
        """Set next calling will affect timeout error"""
        self.timeout = True

    def must_crack(self):
        """Set next calling will affect 500 response"""
        self.internal = True

    def process(self, mockserver):
        """By order of priority: raises timeout error if setted, return 500 or
        response if Ok"""
        if self.timeout:
            self.timeout = False
            raise mockserver.TimeoutError()
        if self.internal or not self.response:
            self.internal = False
            return mockserver.make_response('internal error', status=500)
        if self.content_type == 'application/x-protobuf':
            return mockserver.make_response(
                self.response.SerializeToString(),
                status=200,
                content_type=self.content_type,
            )
        if self.content_type == 'application/x-flatbuffers':
            return mockserver.make_response(
                self.response, status=200, content_type=self.content_type,
            )
        return self.response
