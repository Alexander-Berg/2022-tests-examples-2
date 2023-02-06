import bson
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from metadata_storage_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
async def mock_archive_api(mockserver):
    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _archive_api(request):
        if request.json['query'][0]['id'] == 'test_ns/test_id':
            data = {
                'source': 'test',
                'items': [
                    {
                        'id': 'test_ns/test_id',
                        'updated': 1496252630.763,
                        'experiments': [
                            {
                                'name': 'exp1',
                                'position': 1,
                                'version': 1,
                                'json': '{}',
                                'is_signal': False,
                            },
                            {
                                'name': 'exp2',
                                'position': 3,
                                'version': 2,
                                'json': '{"name1":"val1"}',
                                'is_signal': False,
                            },
                        ],
                        'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
                    },
                ],
            }
        else:
            data = {'source': 'test', 'items': []}
        return mockserver.make_response(
            bson.BSON.encode(data),
            status=200,
            content_type='application/bson',
            charset='utf-8',
        )
