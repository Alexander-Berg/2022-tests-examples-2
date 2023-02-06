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
        self.timeout_always = False
        self.internal = False
        self.internal_always = False
        self.response = None
        self.content_type = None

    def must_timeout(self, always=False):
        """Set next calling will affect timeout error.
        If `always` is set all next calls will affect too"""
        self.timeout = True
        self.timeout_always = always

    def must_crack(self, always=False):
        """Set next calling will affect 500 response.
        If `always` is set all next calls will affect too"""
        self.internal = True
        self.internal_always = always

    def process(self, mockserver):
        """By order of priority: raises timeout error if set, return 500 or
        response if Ok"""
        if self.timeout:
            if not self.timeout_always:
                self.timeout = False
            raise mockserver.TimeoutError()
        if self.internal or not self.response:
            if not self.internal_always:
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
