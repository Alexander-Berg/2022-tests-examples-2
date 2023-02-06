import hashlib

import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import files


async def count_files(taxi_exp_client):
    response = await files.search_file(taxi_exp_client)
    assert response.status == 200
    result = await response.json()
    return len(result['files'])


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
            },
        },
    },
)
async def test_update_trusted_file(taxi_exp_client):
    # upload file
    response = await files.post_file(
        taxi_exp_client, 'non_trusted', b'test_content',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    # found one file
    assert (await count_files(taxi_exp_client)) == 1

    # make file is trusted
    await db.transform_file_to_trusted(
        taxi_exp_client.app, file_id, tag='trusted',
    )

    # found no file
    assert (await count_files(taxi_exp_client)) == 0

    # update trusted file
    response = await files.post_trusted_file(
        taxi_exp_client, 'trusted', b'trusted content',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    # fail to update due to changes exceeding the threshold
    content = b'trusted content\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
    headers = {
        'YaTaxi-Api-Key': 'secret',
        'X-File-Tag': 'trusted',
        'X-Is-Trusted': 'true',
        'Content-Length': str(len(content)),
    }
    response = await taxi_exp_client.post(
        '/v1/files/', headers=headers, data=content,
    )
    assert response.status == 400
    resp_text = await response.text()
    assert (
        resp_text == '{"message": "File lines count significantly '
        'changed", "code": '
        '"TRUSTED_FILES_FILE_LINES_COUNT_SIGNIFICANT_CHANGE"}'
    )

    # get file by tag
    content = await files.get_file_body(taxi_exp_client, file_id)
    assert content == b'trusted content\n'

    response = await files.get_trusted_file_metadata(
        taxi_exp_client, 'trusted',
    )
    assert response.status == 200
    body = await response.json()
    assert body['sha256'] == hashlib.sha256(b'trusted content\n').hexdigest()
