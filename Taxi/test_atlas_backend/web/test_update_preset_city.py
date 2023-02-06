import bson
import pytest


@pytest.mark.parametrize(
    'username,new_cities,expected_status',
    [
        ('omnipotent_user', ['Абакан'], 200),
        ('city_user', ['Абакан'], 403),
        ('city_user', ['Казань'], 200),
    ],
)
async def test_get_update_cities(
        web_app_client,
        db,
        atlas_blackbox_mock,
        username,
        new_cities,
        expected_status,
):
    test_id = '59ee04f28d8d14f5e9d85d76'
    response = await web_app_client.post(
        '/api/preset_cities/update',
        json={'_id': test_id, 'cities': new_cities},
    )
    assert response.status == expected_status, await response.text()

    if response.status != 200:
        return

    content = await response.json()
    assert content['_id'] == test_id and content['response'] == 'ok'

    preset_city = await db.atlas_preset_cities.find_one(
        {'_id': bson.ObjectId(test_id)},
    )

    assert preset_city['cities'] == new_cities
