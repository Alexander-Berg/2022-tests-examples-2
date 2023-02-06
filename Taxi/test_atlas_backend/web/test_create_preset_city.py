import pytest


@pytest.mark.parametrize(
    'username,cities,expected_status',
    [
        ('city_user', ['Москва'], 200),
        ('city_user', ['Москва', 'Казань'], 200),
        ('city_user', ['Владивосток'], 403),
        ('omnipotent_user', ['Владивосток'], 200),
    ],
)
async def test_create_preset_city(
        web_app_client,
        db,
        atlas_blackbox_mock,
        username,
        cities,
        expected_status,
):
    preset_city_json = {
        'user': username,
        'cities': cities,
        'name': 'Тест',
        'public': True,
    }
    response = await web_app_client.post(
        '/api/preset_cities/create', json=preset_city_json,
    )
    assert response.status == expected_status, await response.text()

    if response.status != 200:
        return

    content = await response.json()
    preset_city = await db.atlas_preset_cities.find_one({'eng': 'Test'})
    preset_city_id = preset_city.pop('_id')
    assert (
        content['_id'] == str(preset_city_id) and content['response'] == 'ok'
    )
    preset_city.pop('eng')
    assert preset_city == preset_city_json


async def test_create_clashing_preset(web_app_client, atlas_blackbox_mock):
    preset_city_json = {
        'user': 'omnipotent_user',
        'cities': ['Москва'],
        'name': 'All Cities',
        'public': True,
    }
    response = await web_app_client.post(
        '/api/preset_cities/create', json=preset_city_json,
    )
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content == {
        'code': 'BadRequest::AlreadyExist',
        'message': 'Preset with clashing names already exists',
        'details': {'id': '5ac1e23a8d8d14a883d8caa5'},
    }


async def test_create_preset_city_empty(web_app_client):
    preset_city_json = {
        'user': 'test_user',
        'cities': [],
        'name': 'Тест',
        'public': True,
    }
    response = await web_app_client.post(
        '/api/preset_cities/create', json=preset_city_json,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    expected = {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': (
                'Invalid value for cities: [] number of '
                'items must be greater than or equal to 1'
            ),
        },
    }
    assert content == expected
