import pytest

from test_taxi_exp.helpers import files


@pytest.mark.pgsql('taxi_exp')
async def test_metadata(taxi_exp_client):
    # post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # check metadata
    response = await files.search_file(
        taxi_exp_client, id=first_file_id, limit=1,
    )
    assert response.status == 200
    result = await response.json()
    assert result['files'][0]['metadata'] == {
        'file_format': 'string',
        'file_size': 13,
        'lines': 1,
        'sha256': (
            'fd697d20f5d280279e4bab06823d149db6d1cf176f25c7a7c1cfb58430ee36fa'
        ),
    }
