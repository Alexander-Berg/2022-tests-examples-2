import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import files


@pytest.mark.parametrize(
    'file_name,file_size,file_hash',
    [
        (
            'regular_file.txt',
            66,
            '88b6123e43ad3e0b5baaa38d6c2892db'
            '3f3f02b061c40880e1cc81297fca569a',
        ),
        (
            'file_with_cr_lf_endings.txt',
            66,
            '7dc01abdd45565748d8a70f156b9b5e0'
            '9074c029684a308264eac64394f9ca36',
        ),
        (
            'file_with_spaces.txt',
            68,
            'a1cee6f152e5012009e7ed0c93d56b72'
            'b0ca369b1192262f1d79d7c9088c03ab',
        ),
        (
            'cyrillic.txt',
            168,
            '763ddf0332119461ef0538d71cad4304'
            '10f8a6dd254a936455af7f0817287bc2',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp')
async def test_files(file_name, taxi_exp_client, load, file_size, file_hash):
    body = load(file_name, mode='rb', encoding=None)
    file_type = None
    check = None
    status = 200

    response = await files.post_file(
        taxi_exp_client, 'file.txt', body, file_type=file_type, check=check,
    )
    assert response.status == status
    mds_id = (await response.json())['id']

    if file_name == 'file_with_spaces.txt':
        mds_id = (await response.json())['id']
        response = await files.get_file_body(taxi_exp_client, mds_id)
        assert ' ' in response.decode('utf-8')

    db_metadata = await db.get_file(taxi_exp_client.app, mds_id)
    assert db_metadata['file_size'] == file_size
    assert db_metadata['sha256'] == file_hash
