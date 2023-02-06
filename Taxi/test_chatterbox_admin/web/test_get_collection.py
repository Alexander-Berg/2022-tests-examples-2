import http

import pytest

from chatterbox_admin.common import constants
from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'collection_id,status_code,expected_result',
    (
        (
            const.COLLECTION_UUID_1,
            http.HTTPStatus.OK,
            {
                'active': False,
                'categories': [],
                'id': const.COLLECTION_UUID_1,
                'name': 'awesome collection',
                'description': 'awesome description',
                'files': [
                    {
                        'id': const.FILE_UUID_1,
                        'deleted': False,
                        'description': 'how to be happy',
                        'name': 'file_001.jpeg',
                        'tags': ['happy', 'nice', 'fun'],
                        'url': constants.ATTACH_URL % const.FILE_UUID_1,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_1,
                    },
                    {
                        'deleted': False,
                        'description': 'so sad',
                        'id': const.FILE_UUID_5,
                        'name': 'file_005.jpeg',
                        'tags': ['sad'],
                        'url': constants.ATTACH_URL % const.FILE_UUID_5,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_5,
                    },
                ],
            },
        ),
        (
            const.COLLECTION_UUID_2,
            http.HTTPStatus.OK,
            {
                'active': True,
                'categories': ['taxi', 'eda'],
                'id': const.COLLECTION_UUID_2,
                'name': 'another collection',
                'description': 'beautiful description',
                'files': [
                    {
                        'deleted': False,
                        'description': 'how to be happy',
                        'id': const.FILE_UUID_1,
                        'name': 'file_001.jpeg',
                        'tags': ['happy', 'nice', 'fun'],
                        'url': constants.ATTACH_URL % const.FILE_UUID_1,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_1,
                    },
                    {
                        'deleted': True,
                        'description': 'so close',
                        'id': const.FILE_UUID_2,
                        'name': 'file_002.jpeg',
                        'tags': [],
                        'url': constants.ATTACH_URL % const.FILE_UUID_2,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_2,
                    },
                    {
                        'deleted': False,
                        'description': 'dance penguin',
                        'id': const.FILE_UUID_3,
                        'name': 'file_003.gif',
                        'tags': ['animal', 'fun'],
                        'url': constants.ATTACH_URL % const.FILE_UUID_3,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_3,
                    },
                ],
            },
        ),
        (
            const.COLLECTION_UUID_3,
            http.HTTPStatus.OK,
            {
                'active': True,
                'categories': ['taxi', 'eda'],
                'id': const.COLLECTION_UUID_3,
                'name': 'good collection',
                'description': '',
                'files': [
                    {
                        'deleted': False,
                        'description': 'need some sleep',
                        'id': const.FILE_UUID_6,
                        'name': 'file_006.gif',
                        'tags': [],
                        'url': constants.ATTACH_URL % const.FILE_UUID_6,
                        'preview': constants.PREVIEW_URL % const.FILE_UUID_6,
                    },
                ],
            },
        ),
        (const.COLLECTION_UUID_NOT_EXIST, http.HTTPStatus.NOT_FOUND, None),
        (const.UUID_BAD_FMT, http.HTTPStatus.BAD_REQUEST, None),
    ),
)
async def test_get_collection(
        taxi_chatterbox_admin_web, collection_id, status_code, expected_result,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/attachments/collections', params={'collection_id': collection_id},
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        content = await response.json()
        assert content == expected_result
