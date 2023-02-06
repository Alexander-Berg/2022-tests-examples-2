import json

import pytest


class MediaStorageContext:
    def __init__(self):
        self.urls = {}

    def set_url(self, storage_id, url):
        self.urls['storage:' + storage_id] = url


@pytest.fixture(name='media_storage')
def _media_storage(mockserver):
    context = MediaStorageContext()

    @mockserver.handler('/media-storage/service/driver_photo/v1/retrieve')
    def _service_v1_retrieve(request):
        storage_id = request.args.get('id')

        key = 'storage:' + storage_id
        if key not in context.urls:
            return mockserver.make_response('not found', 404)

        return mockserver.make_response(
            json.dumps({'url': context.urls[key], 'version': 'etag'}), 200,
        )

    return context
