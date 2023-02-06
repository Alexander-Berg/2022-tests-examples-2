import dateutil

from taxi.clients import mds_s3


class MockSession:
    def __init__(self, responses):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get_object(self, **kwargs):
        return self.responses['get_object'](**kwargs)

    async def put_object(self, **kwargs):
        return self.responses['put_object'](**kwargs)

    async def delete_object(self, **kwargs):
        return self.responses['delete_object'](**kwargs)

    async def delete_objects(self, **kwargs):
        return self.responses['delete_objects'](**kwargs)

    async def list_objects(self, **kwargs):
        return self.responses['list_object'](**kwargs)

    async def create_bucket(self, **kwargs):
        return self.responses['create_bucket'](**kwargs)

    async def delete_bucket(self, **kwargs):
        return self.responses['delete_bucket'](**kwargs)

    async def get_buckets(self, **kwargs):
        return self.responses['get_buckets'](**kwargs)

    def create_client(self, *args, **kwargs):
        return self


class FakeBodyStream:
    def __init__(self, data):
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def read(self):
        return self.data


S3_SETTINGS = {
    'url': 'test.mds',
    'bucket': 'test',
    'access_key_id': 'access_key_id',
    'secret_key': 'secret_key',
}


async def test_get_object(monkeypatch):
    e_tag = '89c8ffd4bfb54e0783b9cc14df254a86'
    body = b'\x01\x02'
    last_modified = 'Thu, 02 Aug 2018 12:03:13 GMT'
    content_type = 'image/jpeg'
    content_length = 149759
    mock_session = MockSession(
        {
            'get_object': lambda **kwargs: {
                'ResponseMetadata': {
                    'RequestId': '533aa23ee902d36d',
                    'HostId': '',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders': {
                        'server': 'nginx',
                        'date': 'Thu, 02 Aug 2018 12:23:58 GMT',
                        'content-type': content_type,
                        'content-length': '%d' % content_length,
                        'connection': 'keep-alive',
                        'keep-alive': 'timeout=60',
                        'accept-ranges': 'bytes',
                        'etag': e_tag,
                        'last-modified': last_modified,
                        'x-amz-request-id': '533aa23ee902d36d',
                        'access-control-allow-origin': '*',
                    },
                    'RetryAttempts': 0,
                },
                'AcceptRanges': 'bytes',
                'LastModified': dateutil.parser.parse(last_modified),
                'ContentLength': content_length,
                'ETag': e_tag,
                'ContentType': content_type,
                'Metadata': {},
                'Body': FakeBodyStream(body),
            },
        },
    )
    monkeypatch.setattr(
        mds_s3.aiobotocore,
        'get_session',
        lambda *args, **kwargs: mock_session,
    )
    client = mds_s3.MdsS3Client(S3_SETTINGS)

    key = 'test_key'
    obj = await client.get_object(key)
    assert obj.body == body
    assert obj.key == key
    assert obj.last_modified == dateutil.parser.parse(last_modified)
    assert obj.e_tag == e_tag
    assert obj.size == content_length
    assert obj.content_type == content_type


async def test_download_content(monkeypatch):
    e_tag = '89c8ffd4bfb54e0783b9cc14df254a86'
    body = b'\x01\x02'
    content_type = 'image/jpeg'
    mock_session = MockSession(
        {
            'get_object': lambda **kwargs: {
                'ETag': e_tag,
                'ContentType': content_type,
                'Body': FakeBodyStream(body),
            },
        },
    )
    monkeypatch.setattr(
        mds_s3.aiobotocore,
        'get_session',
        lambda *args, **kwargs: mock_session,
    )
    client = mds_s3.MdsS3Client(S3_SETTINGS)
    assert await client.download_content('test_key') == body


async def test_upload_object(monkeypatch):
    e_tag = '89c8ffd4bfb54e0783b9cc14df254a86'
    body = b'\x01\x02'
    content_type = 'image/jpeg'
    mock_session = MockSession(
        {
            'put_object': lambda **kwargs: {
                'ResponseMetadata': {
                    'RequestId': '4d70315855cebc3c',
                    'HostId': '',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders': {
                        'server': 'nginx',
                        'date': 'Thu, 02 Aug 2018 14:01:01 GMT',
                        'content-length': '0',
                        'connection': 'keep-alive',
                        'keep-alive': 'timeout=60',
                        'x-amz-version-id': 'null',
                        'etag': e_tag,
                        'x-amz-request-id': '4d70315855cebc3c',
                        'access-control-allow-origin': '*',
                    },
                    'RetryAttempts': 0,
                },
                'ETag': e_tag,
                'VersionId': 'null',
            },
        },
    )
    monkeypatch.setattr(
        mds_s3.aiobotocore,
        'get_session',
        lambda *args, **kwargs: mock_session,
    )
    client = mds_s3.MdsS3Client(S3_SETTINGS)

    key = 'test_key'
    obj = await client.upload_content(key, body, content_type)
    assert obj.body is None
    assert obj.key == key
    assert obj.last_modified is None
    assert obj.e_tag == e_tag
    assert obj.content_type is None
