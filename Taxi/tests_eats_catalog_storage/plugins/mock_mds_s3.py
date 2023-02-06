import pytest


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    """
    Copy-paste from media-storage service
    """

    class FakeMdsClient:
        storage = {}

        def put_object(self, key, body):
            self.storage[key] = bytearray(body)

        def get_object(self, key) -> bytearray:
            return self.storage.get(key)

    client = FakeMdsClient()

    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    path_prefix = '/mds-s3'

    def extract_key(request):
        return request.path[len(path_prefix) + 1 :]

    @mockserver.handler(path_prefix, prefix=True)
    def _mock_all(request):
        key = extract_key(request)

        if request.method == 'PUT':
            copy_source = request.headers.get('x-amz-copy-source', None)
            if copy_source is not None:
                dest_bucket = request.headers['Host'].split('.')[0]
                source_bucket, source_key = copy_source.split('/')[1:3]
                # coping between buckets isn't supported yet
                assert source_bucket == dest_bucket

                data = mds_s3_storage.get_object(source_key)
            else:
                data = request.get_data()
            mds_s3_storage.put_object(key, data)
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = mds_s3_storage.get_object(key)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)
