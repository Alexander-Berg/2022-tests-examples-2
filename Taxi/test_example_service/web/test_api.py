from . import common


async def test_int_enum_200(web_app_client):
    response = await web_app_client.post('/int-enum', json={'age': 1})
    assert response.status == 200
    assert await response.json() == {'age_plus_one': 2}


async def test_int_enum_400(web_app_client):
    response = await web_app_client.post('/int-enum', json={'age': 2})
    assert response.status == 400
    assert await response.json() == common.make_request_error(
        'Invalid value for age: 2 must be one of [1]',
    )
