import pytest


@pytest.mark.pgsql('taxi_exp', files=('fill_tags.sql',))
async def test_get_tags(taxi_exp_client):
    response = await taxi_exp_client.get(
        '/v1/trusted-files/tags/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 10, 'offset': 0},
    )
    assert response.status == 200
    result = await response.json()
    assert result['tags'] == ['tag_1', 'tag_2']
