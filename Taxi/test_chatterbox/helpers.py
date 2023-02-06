from taxi.util import callinfo


class BaseAsyncPatcher:
    """
    Base patcher is used for mocking api client method

    Parameters
    :target - object which will be mocked
    :method - method name which will be patched
    :response_body - response which will be returned from mocked function

    example usage:
        >>> client_patcher = BaseAsyncPatcher(ClientApi, 'get_comments')
        >>> client_patcher.patch(monkeypatch)
        >>> client_patcher.set_response('comments body')
        >>> assert ClientApi().get_comments() == 'comments body'
        >>> client_patcher.assert_called()
    """

    def __init__(self, target, method, response_body='default dummy'):
        self.target = target
        self.method = method
        self.response_body = response_body
        self.patched_method = callinfo.CallsInfoWrapper(self.get_method())

    def __str__(self):
        return 'class={} method={} calls={}'.format(
            self.target, self.method, self.calls,
        )

    def set_response(self, body):
        self.response_body = body

    def get_method(self):
        async def get_response_body(*args, **kwargs):
            return self.response_body

        return get_response_body

    def patch(self, monkeypatch):
        monkeypatch.setattr(
            target=self.target, name=self.method, value=self.patched_method,
        )

    @property
    def call(self):
        return self.patched_method.call

    @property
    def calls(self):
        return self.patched_method.calls

    def assert_called(self):
        assert self.calls, '{} is not called'.format(self)
