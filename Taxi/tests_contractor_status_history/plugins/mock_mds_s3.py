import pytest


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    class FakeMdsContext:
        def __init__(self):
            self._storage = {}

        def put_object(self, path, body):
            self._storage[path] = body

        def get_object(self, path):
            return self._storage.get(path)

    context = FakeMdsContext()

    return context


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(request, mockserver, mds_s3_storage):
    marker = request.node.get_closest_marker('fail_s3mds')

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_s3(request):
        if marker:
            data = marker.args[0]
            return mockserver.make_response(data['msg'], data['code'])

        if request.method == 'PUT':
            mds_s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = mds_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
            return mockserver.make_response('NotFound', 404)

        return mockserver.make_response('Wrong Method', 400)
