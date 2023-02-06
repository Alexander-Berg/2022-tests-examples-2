import pytest

from crm_admin.generated.service.swagger import models


EVERY_SALT = '4457b9de118347c696eaa54c97b272f4'
OWNER_OF_ALL = 'test_owner'


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_create_target(web_context, web_app_client):
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target_1',
        name='Fancy Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )

    expected_result = target_body.serialize()
    expected_result['id'] = 1
    expected_result['owner'] = OWNER_OF_ALL
    expected_result['created_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['updated_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['const_salt'] = EVERY_SALT

    assert response.status == 200
    assert expected_result == await response.json()

    target_body.label = expected_result['label'] = 'fancy_target_2'

    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )

    expected_result['id'] = 2
    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_create_minimal_target(web_context, web_app_client):
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target',
        name='Fancy Target',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )

    expected_result = target_body.serialize()
    expected_result['id'] = 1
    expected_result['owner'] = OWNER_OF_ALL
    expected_result['created_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['updated_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['const_salt'] = EVERY_SALT
    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_get_target(web_context, web_app_client):
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target',
        name='Fancy Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200
    target_id = await response.json()
    target_id = target_id['id']

    response = await web_app_client.get(f'/v1/targets/{target_id}')

    expected_result = target_body.serialize()
    expected_result['id'] = 1
    expected_result['owner'] = OWNER_OF_ALL
    expected_result['created_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['updated_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['const_salt'] = EVERY_SALT
    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_update_target(web_context, web_app_client):
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target',
        name='Fancy Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200
    target_id = await response.json()
    target_id = target_id['id']

    target_body.name = 'Ultra Fancy'
    target_body.is_important = False
    target_body.is_available = False
    target_body.description = 'wat'
    target_body.control_settings.is_control_active = False
    target_body.control_settings.track_all = False

    response = await web_app_client.put(
        f'/v1/targets/{target_id}', json=target_body.serialize(),
    )

    expected_result = target_body.serialize()
    expected_result['id'] = 1
    expected_result['owner'] = OWNER_OF_ALL
    expected_result['created_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['updated_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['const_salt'] = EVERY_SALT
    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_update_get_target(web_context, web_app_client):
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target',
        name='Fancy Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200
    target_id = await response.json()
    target_id = target_id['id']

    target_body.name = 'Ultra Fancy'
    target_body.is_important = False
    target_body.is_available = False
    target_body.description = 'wat'
    target_body.control_settings.is_control_active = False
    target_body.control_settings.track_all = False

    response = await web_app_client.put(
        f'/v1/targets/{target_id}', json=target_body.serialize(),
    )
    assert response.status == 200

    response = await web_app_client.get(f'/v1/targets/{target_id}')

    expected_result = target_body.serialize()
    expected_result['id'] = 1
    expected_result['owner'] = OWNER_OF_ALL
    expected_result['created_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['updated_at'] = '2022-02-22T02:22:22+03:00'
    expected_result['const_salt'] = EVERY_SALT
    assert response.status == 200
    assert expected_result == await response.json()
