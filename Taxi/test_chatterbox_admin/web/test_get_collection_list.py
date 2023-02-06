import http

import pytest

from chatterbox_admin.common import constants
from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'categories,status_code,expected_result',
    (
        (
            ['taxi'],
            http.HTTPStatus.OK,
            {
                'collections': [
                    {
                        'id': const.COLLECTION_UUID_2,
                        'name': 'another collection',
                        'description': 'beautiful description',
                        'categories': ['taxi', 'eda'],
                        'active': True,
                        'files': [
                            {
                                'id': const.FILE_UUID_1,
                                'description': 'how to be happy',
                                'name': 'file_001.jpeg',
                                'tags': ['fun', 'happy', 'nice'],
                                'url': (
                                    constants.ATTACH_URL % const.FILE_UUID_1
                                ),
                                'preview': (
                                    constants.PREVIEW_URL % const.FILE_UUID_1
                                ),
                                'deleted': False,
                            },
                            {
                                'id': const.FILE_UUID_3,
                                'description': 'dance penguin',
                                'name': 'file_003.gif',
                                'tags': ['animal', 'fun'],
                                'url': (
                                    constants.ATTACH_URL % const.FILE_UUID_3
                                ),
                                'preview': (
                                    constants.PREVIEW_URL % const.FILE_UUID_3
                                ),
                                'deleted': False,
                            },
                        ],
                    },
                    {
                        'id': const.COLLECTION_UUID_3,
                        'name': 'good collection',
                        'description': '',
                        'categories': ['taxi', 'eda'],
                        'active': True,
                        'files': [
                            {
                                'description': 'need some sleep',
                                'id': const.FILE_UUID_6,
                                'name': 'file_006.gif',
                                'tags': [],
                                'url': (
                                    constants.ATTACH_URL % const.FILE_UUID_6
                                ),
                                'preview': (
                                    constants.PREVIEW_URL % const.FILE_UUID_6
                                ),
                                'deleted': False,
                            },
                        ],
                    },
                ],
            },
        ),
        ([], http.HTTPStatus.BAD_REQUEST, None),
        (['not exists'], http.HTTPStatus.OK, {'collections': []}),
    ),
)
async def test_get_collection_list(
        taxi_chatterbox_admin_web, categories, status_code, expected_result,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/internal/collections', params={'categories': categories},
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        content = await response.json()
        assert content == expected_result
