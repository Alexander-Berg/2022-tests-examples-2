import copy

import pytest

from tests_zalogin import utils


async def test_invalid_user_id(taxi_zalogin, mockserver):
    invalid_user_id = '111'
    user_id = '11111111111111111111111111111111'

    @mockserver.json_handler('/user-api/v3/users/create')
    def _user_api_users_create(request):
        return {'id': user_id}

    response = await taxi_zalogin.post(
        'v1/launch/auth', json={'id': invalid_user_id},
    )
    assert response.status_code == 200
    assert utils.without_fields(response.json(), 'uuid') == utils.with_ids(
        utils.build_expected_response(), user_id=user_id,
    )


async def test_uuid_in_query(taxi_zalogin, mockserver):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    uuid_in_query = '3333333333333333333333333333333a'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(), user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json == utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=uuid_in_query,
        )
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth', params={'uuid': uuid_in_query}, json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=uuid_in_query,
    )


@pytest.mark.parametrize('use_uuid_from_header', [True, False])
async def test_use_uuid_from_header(
        taxi_zalogin, mockserver, taxi_config, use_uuid_from_header,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    uuid_in_query = '3333333333333333333333333333333a'
    uuid_in_header = '4444444444444444444444444444444b'

    taxi_config.set(ZALOGIN_USE_UUID_FROM_HEADER=use_uuid_from_header)

    expected_uuid = uuid_in_header if use_uuid_from_header else uuid_in_query

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(), user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json == utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=expected_uuid,
        )
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        headers={'X-AppMetrica-UUID': uuid_in_header},
        params={'uuid': uuid_in_query},
        json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=expected_uuid,
    )


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


@pytest.mark.parametrize(
    'uuid_in_query',
    [
        '222',
        '2222222222222222222222222222222?',
        '2222222222222222222222222222222A',
    ],
)
async def test_invalid_uuid_in_query(taxi_zalogin, mockserver, uuid_in_query):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(), user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json == utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
        )
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth', params={'uuid': uuid_in_query}, json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=yandex_uuid,
    )


@pytest.mark.parametrize('params', [None, {'uuid': '333'}])
async def test_no_yandex_uuid_in_db(taxi_zalogin, mockserver, params):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = None

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(utils.build_userinfo(), user_id=user_id)

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        nonlocal yandex_uuid
        yandex_uuid = request.json['yandex_uuid']
        assert len(yandex_uuid) == 32
        assert utils.without_fields(
            request.json, 'yandex_uuid',
        ) == utils.with_ids(utils.build_users_request(), user_id=user_id)
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth', params=params, json={'id': user_id},
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=yandex_uuid,
    )


@pytest.mark.parametrize(
    'request_user_id', [None, 'z1111111111111111111111111111111'],
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_drop_uuid(taxi_zalogin, request_user_id):
    uuid_in_query = '22222222222222222222222222222222'

    request_body = {}
    if request_user_id is not None:
        request_body['id'] = request_user_id

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'uuid': uuid_in_query},
        headers={
            'X-Request-Application': 'app_name=iphone,app_ver1=4,app_ver2=90',
        },
        json=request_body,
    )
    assert response.status_code == 200
    assert 'uuid' not in response.json()


@pytest.mark.parametrize(
    'request_user_id', [None, '33333333333333333333333333333333'],
)
@pytest.mark.parametrize('zuser_enabled', [True, False])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_new_user_id(
        taxi_zalogin, mockserver, request_user_id, zuser_enabled,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    app_ver = '90' if zuser_enabled else '89'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'NOT_FOUND', 'message': 'user object not found'},
        )

    @mockserver.json_handler('/user-api/v3/users/create')
    def _user_api_users_create(request):
        return {'id': user_id}

    request_body = {}
    if request_user_id is not None:
        request_body['id'] = request_user_id

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'uuid': yandex_uuid},
        headers={
            'X-Request-Application': (
                f'app_name=iphone,app_ver1=4,app_ver2={app_ver}'
            ),
        },
        json=request_body,
    )
    assert response.status_code == 200

    response_body = response.json()

    if zuser_enabled:
        user_id = response_body['id']
        assert len(user_id) == 32 and user_id[0] == 'z'
        assert (
            utils.without_fields(response_body, 'id')
            == utils.build_expected_response()
        )
        assert _user_api_users_create.times_called == 0
    else:
        assert response_body == utils.with_ids(
            utils.build_expected_response(), user_id=user_id, uuid=yandex_uuid,
        )
        assert _user_api_users_create.times_called == 1

    if request_user_id is None:
        assert _user_api_userinfo.times_called == 0
    else:
        assert _user_api_userinfo.times_called == 1


@pytest.mark.parametrize('zuser_enabled', [True, False])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_zuser(taxi_zalogin, mockserver, zuser_enabled):
    user_id = '11111111111111111111111111111111'
    zuser_id = 'z1111111111111111111111111111111'
    app_ver = '90' if zuser_enabled else '89'

    @mockserver.json_handler('/user-api/v3/users/create')
    def _user_api_users_create(request):
        return {'id': user_id}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        headers={
            'X-Request-Application': (
                f'app_name=iphone,app_ver1=4,app_ver2={app_ver}'
            ),
        },
        json={'id': zuser_id},
    )
    assert response.status_code == 200
    if zuser_enabled:
        assert response.json() == utils.with_ids(
            utils.build_expected_response(), user_id=zuser_id,
        )
        assert _user_api_users_create.times_called == 0
    else:
        assert utils.without_fields(response.json(), 'uuid') == utils.with_ids(
            utils.build_expected_response(), user_id=user_id,
        )
        assert _user_api_users_create.times_called == 1


@pytest.mark.parametrize(
    'zuser_enabled, token_only',
    [(True, False), (True, True), (False, True), (False, False)],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='exp3_exchange_user_for_zuser.json')
async def test_exchange_user_for_zuser(
        taxi_zalogin, mockserver, zuser_enabled, token_only,
):
    # case when we have no token
    user_id = '11111111111111111111111111111111'
    app_ver = '90' if zuser_enabled else '89'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        assert request.json == {'id': user_id}
        return utils.with_ids(
            utils.build_userinfo(token_only=token_only), user_id=user_id,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json['id'] == user_id
        assert request.json['authorized'] is False
        return {}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        headers={
            'X-Request-Application': (
                f'app_name=iphone,app_ver1=4,app_ver2={app_ver}'
            ),
        },
        json={'id': user_id},
    )
    assert response.status_code == 200
    response_body = response.json()

    if zuser_enabled and token_only:
        user_id = response_body['id']
        assert len(user_id) == 32 and user_id[0] == 'z'
        assert (
            utils.without_fields(response_body, 'id', 'uuid')
            == utils.build_expected_response()
        )
        assert _user_api_users_update.times_called == 1
    else:
        assert utils.without_fields(response.json(), 'uuid') == utils.with_ids(
            utils.build_expected_response(), user_id=user_id,
        )
        assert _user_api_users_update.times_called == 1


@pytest.mark.parametrize('new_user', [True, False])
async def test_create_or_update_user(taxi_zalogin, mockserver, new_user):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        assert request.json == {'id': user_id}
        return utils.with_ids(
            utils.build_userinfo(), user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/create')
    def _user_api_users_create(request):
        assert request.json == utils.with_ids(
            utils.build_users_request(
                has_ya_plus=False, has_cashback_plus=False, yandex_staff=False,
            ),
            yandex_uuid=yandex_uuid,
        )
        return utils.with_ids({}, user_id=user_id)

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json == utils.with_ids(
            utils.build_users_request(),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
        )
        return {}

    request_body = {}
    if not new_user:
        request_body['id'] = user_id

    response = await taxi_zalogin.post(
        'v1/launch/auth', params={'uuid': yandex_uuid}, json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == utils.with_ids(
        utils.build_expected_response(), user_id=user_id, uuid=yandex_uuid,
    )

    if new_user:
        assert _user_api_userinfo.times_called == 0
        assert _user_api_users_create.times_called == 1
        assert _user_api_users_update.times_called == 0
    else:
        assert _user_api_userinfo.times_called == 1
        assert _user_api_users_create.times_called == 0
        assert _user_api_users_update.times_called == 1


@pytest.mark.parametrize('new_user', [True, False])
async def test_user_fields(taxi_zalogin, mockserver, new_user):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'
    metrica_device_id = 'metrica_device_id'
    app_name = 'test_app'
    app_ver1 = '1'
    app_ver2 = '2'
    app_ver3 = '3'
    request_body = {
        'device_id': 'test_device_id',
        'apns_token': 'test_apns_token',
        'apns_type': 'test_apns_type',
        'gcm_token': 'test_gcm_token',
        'antifraud': {
            'user_id': 'test_user_id',
            'application': 'test_application',
            'application_version': 'test_application_version',
            'yandex_uid': 'test_yandex_uid',
            'yandex_uuid': 'test_yandex_uuid',
            'device_id': 'test_device_id',
            'metrica_uuid': 'test_metrica_uuid',
            'metrica_device_id': 'test_metrica_device_id',
            'instance_id': 'test_instance_id',
            'ip': 'test_ip',
            'mac': 'test_mac',
            'user_phone': 'test_user_phone',
            'zone': 'test_zone',
            'position': {'dx': 123, 'lon': 456.777, 'lat': 789.333},
            'order_id': 'test_order_id',
            'started_in_emulator': True,
        },
    }

    def _change_antifraud(doc):
        res = copy.deepcopy(doc)
        position = res.get('antifraud', {}).get('position')
        if position:
            position['point'] = [position.pop('lon'), position.pop('lat')]
        return res

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(utils.build_userinfo(), user_id=user_id)

    @mockserver.json_handler('/user-api/v3/users/create')
    def _user_api_users_create(request):
        expected_request_body = utils.with_ids(
            utils.build_users_request(
                application=app_name,
                application_version=f'{app_ver1}.{app_ver2}.{app_ver3}',
                has_ya_plus=False,
                has_cashback_plus=False,
                yandex_staff=False,
                metrica_device_id=metrica_device_id,
            ),
            yandex_uuid=yandex_uuid,
        )
        expected_request_body.update(_change_antifraud(request_body))
        assert request.json == expected_request_body
        return utils.with_ids({}, user_id=user_id)

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        expected_request_body = utils.with_ids(
            utils.build_users_request(
                application=app_name,
                application_version=f'{app_ver1}.{app_ver2}.{app_ver3}',
                metrica_device_id=metrica_device_id,
            ),
            user_id=user_id,
            yandex_uuid=yandex_uuid,
        )
        expected_request_body.update(_change_antifraud(request_body))
        assert request.json == expected_request_body
        return {}

    if not new_user:
        request_body['id'] = user_id

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'uuid': yandex_uuid, 'metrica_device_id': metrica_device_id},
        headers={
            'X-Request-Application': (
                f'app_name={app_name},'
                f'app_ver1={app_ver1},app_ver2={app_ver2},app_ver3={app_ver3}'
            ),
        },
        json=request_body,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'userinfo_response, users_update_request, expected_response',
    [
        (  # not authorized
            utils.build_userinfo(),
            utils.build_users_request(),
            utils.build_expected_response(),
        ),
        (  # authorized
            utils.build_userinfo(authorized=True),
            utils.build_users_request(authorized=True),
            utils.build_expected_response(authorized=True),
        ),
        (  # token_only, not authorized
            utils.build_userinfo(token_only=True),
            utils.build_users_request(),
            utils.build_expected_response(),
        ),
        (  # token_only, authorized
            utils.build_userinfo(token_only=True, authorized=True),
            utils.build_users_request(),
            utils.build_expected_response(),
        ),
    ],
)
async def test_no_credentials(
        taxi_zalogin,
        mockserver,
        userinfo_response,
        users_update_request,
        expected_response,
):
    user_id = '11111111111111111111111111111111'
    yandex_uuid = '22222222222222222222222222222222'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        assert request.json == {'id': user_id}
        return utils.with_ids(
            userinfo_response, user_id=user_id, yandex_uuid=yandex_uuid,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        assert request.json == utils.with_ids(
            users_update_request, user_id=user_id, yandex_uuid=yandex_uuid,
        )
        return {}

    response = await taxi_zalogin.post('v1/launch/auth', json={'id': user_id})
    assert response.status_code == 200
    assert utils.without_fields(response.json(), 'uuid') == utils.with_ids(
        expected_response, user_id=user_id,
    )


@pytest.mark.parametrize('loyal', [None, True, False])
async def test_no_credentials_phone(taxi_zalogin, mockserver, loyal):
    user_id = '11111111111111111111111111111111'
    phone_id = '777777777777777777777777'
    phone_personal_id = '33333333333333333333333333333333'
    phone = '+70001112233'
    last_order_nearest_zone = 'moscow'

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_api_userinfo(request):
        return utils.with_ids(
            utils.build_userinfo(
                phone_personal_id=phone_personal_id,
                phone_loyal=loyal,
                last_order_nearest_zone=last_order_nearest_zone,
            ),
            user_id=user_id,
        )

    @mockserver.json_handler('/user-api/v3/users/update')
    def _user_api_users_update(request):
        return {}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _personal_phones_retrieve(request):
        assert request.json == {
            'id': phone_personal_id,
            'primary_replica': False,
        }
        return {'id': phone_personal_id, 'value': phone}

    response = await taxi_zalogin.post('v1/launch/auth', json={'id': user_id})
    assert response.status_code == 200
    assert utils.without_fields(response.json(), 'uuid') == utils.with_ids(
        utils.build_expected_response(
            phone=phone,
            loyal=loyal,
            last_order_nearest_zone=last_order_nearest_zone,
        ),
        user_id=user_id,
        phone_id=phone_id,
        personal_phone_id=phone_personal_id,
    )

    assert _personal_phones_retrieve.times_called == 1
