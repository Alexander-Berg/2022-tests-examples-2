import aiobotocore

from eats_report_sender.services import mds3_service


MDS3Service = mds3_service.MDS3Service


class MockSession:
    def __init__(self, responses):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get_paginator(self, **kwargs):
        return self.responses['get_paginator'](**kwargs)

    async def get_object(self, **kwargs):
        return self.responses['get_object'](**kwargs)

    async def put_object(self, **kwargs):
        return self.responses['put_object'](**kwargs)

    async def delete_object(self, **kwargs):
        return self.responses['delete_object'](**kwargs)

    async def delete_objects(self, **kwargs):
        return self.responses['delete_objects'](**kwargs)

    async def list_objects(self, **kwargs):
        return self.responses['list_objects'](**kwargs)

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


async def test_mds3_service_get_files_as_links(
        stq3_context, report_object, load_json,
):

    service = MDS3Service(stq3_context, report_object)

    result = await service.get_files_as_links(
        ['directory/file_1.json', 'directory/file_2.json'],
    )

    # TODO: research how to use $match in json_loads
    assert len(result) == 2


async def test_mds3_service_get_files_list(
        stq3_context, report_object, monkeypatch,
):

    monkeypatch.setattr(
        aiobotocore,
        'get_session',
        lambda *args, **kwargs: MockSession(
            {
                'list_objects': lambda **kwargs: {
                    'Contents': [
                        {'Key': 'directory/file_1.json'},
                        {'Key': 'directory/file_2.json'},
                    ],
                },
            },
        ),
    )

    service = MDS3Service(stq3_context, report_object)

    results = await service.get_files_list()

    assert results == ['directory/file_1.json', 'directory/file_2.json']


async def test_mds3_service_get_files_as_base64(
        stq3_context, report_object, monkeypatch,
):

    return_data_mapping = {
        'directory/file_1.json': b'content',
        'directory/file_2.json': b'data',
    }

    monkeypatch.setattr(
        aiobotocore,
        'get_session',
        lambda *args, **kwargs: MockSession(
            {
                'get_object': lambda **kwargs: {
                    'Body': FakeBodyStream(return_data_mapping[kwargs['Key']]),
                },
            },
        ),
    )

    service = MDS3Service(stq3_context, report_object)

    result = await service.get_files_as_base64(
        ['directory/file_1.json', 'directory/file_2.json'],
    )

    assert result == [
        mds3_service.Base64File(
            key='directory/file_1.json', data='Y29udGVudA==',
        ),
        mds3_service.Base64File(key='directory/file_2.json', data='ZGF0YQ=='),
    ]
