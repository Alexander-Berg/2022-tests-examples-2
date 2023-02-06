import http

import pytest

from chatterbox_admin.common import constants
from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'file_id,preview,status_code',
    (
        (const.FILE_UUID_1, False, http.HTTPStatus.OK),
        (const.FILE_UUID_1, True, http.HTTPStatus.OK),
        (const.FILE_UUID_NOT_EXIST, False, http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, False, http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_get_file(
        taxi_chatterbox_admin_web, file_id, preview, status_code,
):
    params = {'file_id': file_id}
    if preview:
        params['preview'] = True
    response = await taxi_chatterbox_admin_web.get(
        '/v1/attachments/files', params=params,
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        assert 'X-Accel-Redirect' in response.headers
        assert (
            f'/attachments/'
            f'{constants.ATTACH_PREFIX}/{file_id}'
            in response.headers['X-Accel-Redirect']
        )
