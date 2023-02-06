import pytest


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    class FakeMdsClient:
        storage = {}

        def put_object(self, key, body):
            assert key.startswith('/mds-s3/documents/'), key
            assert body == b'PDF FILE MOCK'
            self.storage[key] = bytearray(b'PDF FILE MOCK')

        def get_object(self, key) -> bytearray:
            assert key.startswith('/mds-s3/documents/'), key
            return self.storage.get(key)

    client = FakeMdsClient()
    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_all(request):
        if request.method == 'PUT':
            mds_s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = mds_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)
