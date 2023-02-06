import hashlib

import pytest

from test_taxi_exp.helpers import files


@pytest.mark.config(
    EXP3_S3_REDIRECT_SETTINGS={
        'enabled': False,
        'force_for_files': ['file.txt'],
    },
)
@pytest.mark.pgsql('taxi_exp')
async def test_redirect_to_s3(taxi_exp_client):
    response = await files.post_file(
        taxi_exp_client, 'file.txt', b'test_content',
    )
    assert response.status == 200
    file_id = (await response.json())['id']
    response = await files.get_file_redirect(
        taxi_exp_client, file_id, allow_s3=True,
    )
    assert (
        response.headers['X-Content-Hash']
        == hashlib.sha256(b'test_content\n').hexdigest()
    )
    assert 'X-Use-S3' in response.headers
    assert response.headers['X-Use-S3'] == 'true'
