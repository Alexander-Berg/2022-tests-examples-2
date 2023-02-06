import http

import pytest

from chatterbox_admin.common import constants
from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'status_code,expected_result',
    (
        (
            http.HTTPStatus.OK,
            [
                {
                    'id': const.FILE_UUID_1,
                    'deleted': False,
                    'description': 'how to be happy',
                    'name': 'file_001.jpeg',
                    'tags': ['happy', 'fun', 'nice'],
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
                    'tags': ['fun', 'animal'],
                    'url': constants.ATTACH_URL % const.FILE_UUID_3,
                    'preview': constants.PREVIEW_URL % const.FILE_UUID_3,
                },
                {
                    'deleted': False,
                    'description': 'need some sleep',
                    'id': const.FILE_UUID_4,
                    'name': 'file_004.gif',
                    'tags': ['sad'],
                    'url': constants.ATTACH_URL % const.FILE_UUID_4,
                    'preview': constants.PREVIEW_URL % const.FILE_UUID_4,
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
        ),
    ),
)
async def test_get_files(
        taxi_chatterbox_admin_web, status_code, expected_result,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/attachments/files/get_all',
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        content = await response.json()
        assert content == expected_result
