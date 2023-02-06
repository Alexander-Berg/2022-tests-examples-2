import pytest


async def test_type_list(web_app_client):
    response = await web_app_client.get('/v1/types/')
    assert response.status == 200
    data = await response.json()

    assert data == {'types': []}


@pytest.mark.parametrize(
    'params,expects',
    [
        ({}, ['more', 'some', 'test']),
        ({'limit': 1}, ['more']),
        ({'offset': 1}, ['some', 'test']),
        ({'type': 'om'}, ['some']),
    ],
)
async def test_type_list_with_params(web_app_client, mongo, params, expects):
    await mongo.log_types.insert_many(
        [{'name': 'more'}, {'name': 'some'}, {'name': 'test'}],
    )

    response = await web_app_client.get('/v1/types/', params=params)
    assert response.status == 200
    data = await response.json()
    assert data['types'] == expects
