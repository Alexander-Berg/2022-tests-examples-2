import pytest

from taxi_tests.utils import callinfo


class TestPointSession:
    def __init__(self):
        self.handlers = {}

    def __getitem__(self, name):
        return self.handlers[name]

    def __call__(self, name):
        def decorator(func):
            wrapped = callinfo.acallqueue(func)
            self.handlers[name] = wrapped
            return wrapped

        return decorator

    async def handle(self, body):
        name = body['name']
        if name in self.handlers:
            data = await self.handlers[name](body['data'])
        else:
            data = None
        return {'data': data}


@pytest.fixture
def testpoint(mockserver):
    session = TestPointSession()

    @mockserver.json_handler('/testpoint')
    async def handler(request):
        return await session.handle(request.json)

    return session
