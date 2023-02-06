# pylint: disable=too-many-statements
from test_taxi_exp.helpers import files


async def test_files(taxi_exp_client):
    # 1. post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content\ntest_2',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # 2. downloading file
    content = await files.get_file_body(taxi_exp_client, first_file_id)
    assert content == b'test_content\ntest_2\n'

    # 3. trying to success put
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'12345', file_type='int',
    )
    assert response.status == 409
    data = await response.json()
    assert data['message'] == (
        'when you update the file version, '
        'the type must be the same. need: string, found: integer'
    )
