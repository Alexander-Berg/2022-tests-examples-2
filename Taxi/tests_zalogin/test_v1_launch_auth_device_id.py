import pytest

from tests_zalogin import utils


@pytest.mark.parametrize('use_metrica_device_id_from_header', [True, False])
async def test_use_metrica_device_id_from_header(
        taxi_zalogin,
        mockserver,
        taxi_config,
        use_metrica_device_id_from_header,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    metrica_device_id_in_query = '3333333333333333333333333333333a'
    metrica_device_id_in_header = '4444444444444444444444444444444b'

    taxi_config.set(
        ZALOGIN_USE_DEVICE_ID_FROM_HEADER=use_metrica_device_id_from_header,
    )

    expected_metrica_device_id = (
        metrica_device_id_in_header
        if use_metrica_device_id_from_header
        else metrica_device_id_in_query
    )

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(), user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        expected = utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
            metrica_device_id=expected_metrica_device_id,
        )
        assert request.json == expected
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        headers={'X-AppMetrica-DeviceId': metrica_device_id_in_header},
        params={'metrica_device_id': metrica_device_id_in_query},
        json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=yandex_uuid,
    )


@pytest.mark.experiments3(filename='exp3_use_device_id_from_metrica.json')
async def test_use_device_id_from_metrica(
        taxi_zalogin, mockserver, taxi_config,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    metrica_device_id = '44444444444444444444444444444444'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(name='test_name'),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        expected = utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
            device_id=metrica_device_id,
            metrica_device_id=metrica_device_id,
        )
        assert request.json == expected
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'metrica_device_id': metrica_device_id},
        json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(name='test_name'),
        user_id=user_id,
        uuid=yandex_uuid,
        device_id=metrica_device_id,
    )


@pytest.mark.parametrize(
    'body_device_id, user_device_id',
    [('device_id1', 'device_id2'), (None, 'device_id1'), (None, None)],
)
async def test_use_device_id_from_user_api(
        taxi_zalogin, mockserver, taxi_config, body_device_id, user_device_id,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
            device_id=user_device_id,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        expected = utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
            device_id=body_device_id,
        )
        assert request.json == expected
        return {}

    resp_body = {'id': user_id}
    if body_device_id is not None:
        resp_body['device_id'] = body_device_id
    response = await taxi_zalogin.post('v1/launch/auth', json=resp_body)
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(),
        user_id=user_id,
        uuid=yandex_uuid,
        device_id=(
            body_device_id if body_device_id is not None else user_device_id
        ),
    )
