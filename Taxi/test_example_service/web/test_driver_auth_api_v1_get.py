async def test_driver_auth_api_v1_old(web_app_client):
    response = await web_app_client.get(
        '/driver-auth/api-v1',
        headers={
            'X-Request-Application-Version': '13.37 (9731)',
            'X-Request-Version-Type': 'x',
            'X-Request-Platform': 'ios',
            'X-YaTaxi-Driver-Profile-Id': 'driver_profile_id',
            'X-YaTaxi-Park-Id': 'park_id',
        },
    )

    assert response.status == 200
    assert (await response.json()) == {
        'brand': 'yandex',
        'build_type': 'x',
        'driver_profile_id': 'driver_profile_id',
        'park_id': 'park_id',
        'platform': 'ios',
        'version': '13.37 (9731)',
        'version_type': 'x',
    }


async def test_driver_auth_api_v1(web_app_client):
    response = await web_app_client.get(
        '/driver-auth/api-v1',
        headers={
            'X-Request-Application-Version': '13.37 (9731)',
            'X-Request-Platform': 'ios',
            'X-Request-Platform-Version': '13.14.15',
            'X-Request-Application-Brand': 'yango',
            'X-Request-Application-Build-Type': 'x',
            'X-Yandex-UID': 'yanxed_uid',
            'X-YaTaxi-Driver-Profile-Id': 'driver_profile_id',
            'X-YaTaxi-Park-Id': 'park_id',
        },
    )

    assert response.status == 200
    assert (await response.json()) == {
        'brand': 'yango',
        'build_type': 'x',
        'driver_profile_id': 'driver_profile_id',
        'park_id': 'park_id',
        'platform': 'ios',
        'platform_version': '13.14.15',
        'version': '13.37 (9731)',
        'version_type': 'yango',
        'yandex_uid': 'yanxed_uid',
    }


async def test_driver_auth_api_v1_unauthorized(web_app_client):
    response = await web_app_client.get(
        '/driver-auth/api-v1',
        headers={
            'X-Request-Application-Version': '13.37 (9731)',
            'X-Request-Version-Type': 'x',
            'X-Request-Platform': 'ios',
        },
    )

    assert response.status == 200
    assert (await response.json()) == {
        'brand': 'yandex',
        'build_type': 'x',
        'platform': 'ios',
        'version': '13.37 (9731)',
        'version_type': 'x',
    }


async def test_driver_auth_api_v1_miscfg_proxy(web_app_client):
    response = await web_app_client.get('/driver-auth/api-v1')

    assert response.status == 500
    assert (await response.json()) == {
        'code': 'driver-authproxy-error',
        'details': ['X-Request-Application-Version header not set'],
        'message': 'error in parsing driver authproxy parameters',
    }


async def test_driver_auth_api_v1_miscfg_local(web_app_client):
    response = await web_app_client.get(
        '/driver-auth/misconfigured-api-v1',
        headers={
            'X-Request-Application-Version': '13.37 (9731)',
            'X-Request-Version-Type': 'x',
            'X-Request-Platform': 'ios',
            'X-YaTaxi-Driver-Profile-Id': 'driver_profile_id',
            'X-YaTaxi-Park-Id': 'park_id',
        },
    )

    assert response.status == 500
    assert (await response.json()) == {
        'code': 'driver-authproxy-configuration-error',
        'details': (
            'Set x-taxi-middlewares.tvm to yes '
            'in handlers that you want to '
            'use with driver-authorization: api-v1'
        ),
        'message': 'driver authproxy has to be used with tvm middleware',
    }
