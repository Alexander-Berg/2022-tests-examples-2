# pylint: disable=too-many-lines

import datetime
import itertools

import psycopg2
import pytest

from . import conftest
from . import utils_v2


async def test_simple(taxi_cargo_claims, state_controller, check_v2_response):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')

    assert claim_info.current_state.point_id == claim_info.points[0].api_id

    check_v2_response(
        request=utils_v2.get_create_request(),
        response=claim_info.claim_full_response,
    )


@pytest.mark.parametrize(
    'request_json, code, message',
    [
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+79098887777',
                },
                'items': [
                    {
                        'title': 'item title 1',
                        'extra_id': '1',
                        'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                        'cost_value': '10.40',
                        'cost_currency': 'RUB',
                        'weight': 10.2,
                        'pickup_point': 1,
                        'droppof_point': 2,
                        'quantity': 2,
                    },
                ],
                'route_points': utils_v2.get_request_points(),
            },
            'invalid_destination_point',
            'No items with such destination point = 3',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+79098887777',
                },
                'items': [
                    {
                        'title': 'item title 1',
                        'extra_id': '1',
                        'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                        'cost_value': '100000000000000000.40000000000000',
                        'cost_currency': 'RUB',
                        'weight': 10.2,
                        'pickup_point': 1,
                        'droppof_point': 2,
                        'quantity': 2,
                    },
                ],
                'route_points': utils_v2.get_request_points(),
            },
            'validation_error',
            'Некорректное значение цены',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+79098887777',
                },
                'items': [
                    {
                        'title': 'item title 1',
                        'extra_id': '1',
                        'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                        'cost_value': '5e+25',
                        'cost_currency': 'RUB',
                        'weight': 10.2,
                        'pickup_point': 1,
                        'droppof_point': 2,
                        'quantity': 2,
                    },
                ],
                'route_points': utils_v2.get_request_points(),
            },
            'validation_error',
            'Некорректное значение цены',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+79098887777',
                },
                'items': utils_v2.get_request_items(),
                'route_points': [
                    {
                        'point_id': 1,
                        'visit_order': 1,
                        'address': {
                            'fullname': '1',
                            'coordinates': [37.8, 55.4],
                            'country': '1',
                            'city': '1',
                            'building_name': '1',
                            'street': '1',
                            'building': '1',
                        },
                        'contact': {
                            'phone': '+79999999991',
                            'name': 'string',
                            'email': '1@yandex.ru',
                        },
                        'type': 'source',
                    },
                    {
                        'point_id': 2,
                        'visit_order': 2,
                        'address': {
                            'fullname': '2',
                            'coordinates': [37.8, 55.4],
                            'country': '2',
                            'city': '2',
                            'building_name': '2',
                            'street': '2',
                            'building': '2',
                        },
                        'contact': {'phone': '+79999999992', 'name': 'string'},
                        'type': 'destination',
                    },
                    {
                        'point_id': 3,
                        'visit_order': 3,
                        'address': {
                            'fullname': '3',
                            'coordinates': [37.8, 55.4],
                            'country': '3',
                            'city': '3',
                            'building_name': '3',
                            'street': '3',
                            'building': '3',
                        },
                        'contact': {
                            'phone': '+79999999993',
                            'name': 'string',
                            'email': '3@yandex.ru',
                        },
                        'type': 'return',
                    },
                ],
            },
            'item_destination_point_not_found',
            'Item item title 2 droppoff point not found',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+89098887777',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
            'country_phone_code_not_supported',
            'Неверный формат контактного телефона',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+79098887777',
                },
                'items': utils_v2.get_request_items(),
                'route_points': [
                    {
                        'point_id': 1,
                        'visit_order': 1,
                        'address': {
                            'fullname': '1',
                            'coordinates': [37.2, 55.8],
                            'country': '1',
                            'city': '1',
                            'building_name': '1',
                            'street': '1',
                            'building': '1',
                            'door_code': 'door_1',
                            'door_code_extra': 'door_1_extra',
                            'doorbell_name': '1',
                            'comment': 'comment_1',
                        },
                        'contact': {
                            'phone': '+79999999991',
                            'name': 'string',
                            'email': '1@yandex.ru',
                        },
                        'type': 'source',
                        'skip_confirmation': False,
                        'leave_under_door': False,
                        'meet_outside': False,
                        'no_door_call': False,
                        'modifier_age_check': False,
                    },
                    {
                        'point_id': 2,
                        'visit_order': 2,
                        'address': {
                            'fullname': '2',
                            'coordinates': [37.0, 55.8],
                            'country': '2',
                            'city': '2',
                            'building_name': '2',
                            'street': '2',
                            'building': '2',
                            'door_code': 'door_2',
                            'door_code_extra': 'door_2_extra',
                            'doorbell_name': '2',
                            'comment': 'comment_2',
                        },
                        'contact': {'phone': '+79999999992', 'name': 'string'},
                        'type': 'destination',
                        'skip_confirmation': False,
                        'leave_under_door': True,
                        'meet_outside': True,
                        'no_door_call': True,
                        'modifier_age_check': True,
                        'external_order_id': 'external_order_id_1',
                    },
                    {
                        'point_id': 3,
                        'visit_order': 3,
                        'address': {
                            'fullname': '3',
                            'coordinates': [37.0, 55.0],
                            'country': '3',
                            'city': '3',
                            'building_name': '3',
                            'street': '3',
                            'building': '3',
                            'door_code': 'door_3',
                            'door_code_extra': 'door_3_extra',
                            'doorbell_name': '3',
                            'comment': 'comment_3',
                        },
                        'contact': {
                            'phone': '+89999999993',
                            'name': 'string',
                            'email': '3@yandex.ru',
                        },
                        'type': 'destination',
                        'skip_confirmation': False,
                        'leave_under_door': False,
                        'meet_outside': False,
                        'no_door_call': False,
                        'modifier_age_check': False,
                        'external_order_id': 'external_order_id_2',
                    },
                ],
            },
            'country_phone_code_not_supported',
            'Неверный формат телефона для точки маршрута номер 3',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+7909111111111',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
            'invalid_phone_size_incorrect',
            'Неверный формат контактного телефона',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+00001111111',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
            'country_phone_code_not_supported',
            'Неверный формат контактного телефона',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+7909aaaabbcc',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
            'invalid_phone_incorrect_symbol',
            'Неверный формат контактного телефона',
        ),
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '07909aaaabbcc',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
            'invalid_phone_must_start_plus_symbol',
            'Неверный формат контактного телефона',
        ),
    ],
)
async def test_validation_errors(
        taxi_cargo_claims, get_default_headers, request_json, code, message,
):
    headers = get_default_headers()

    request_id = conftest.get_default_idempotency_token()
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/create?request_id={request_id}',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {'message': message, 'code': code}


async def test_create_with_features(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request()
    request['features'] = [{'id': 'feature1'}, {'id': 'feature2'}]
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert sorted(
        response.json()['features'], key=lambda feature: feature['id'],
    ) == sorted(request['features'], key=lambda feature: feature['id'])


async def test_yandex_login(taxi_cargo_claims, get_default_headers, pgsql):
    request = utils_v2.get_create_request()
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
    SELECT yandex_login FROM cargo_claims.claims
        """,
    )
    assert list(cursor) == [('abacaba',)]


async def test_create_v2_no_email(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request()

    for point in request['route_points']:
        if 'email' in point['contact']:
            point['contact'].pop('email', None)
            break

    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )
    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.get(
        f'/v2/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        f'v2/admin/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200


async def test_create_v2_no_emergency(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request()

    request.pop('emergency_contact')

    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )
    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.get(
        f'/v2/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        f'v2/admin/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200


async def test_create_v2_zero_lon_and_lat(
        taxi_cargo_claims, get_default_headers,
):
    request = utils_v2.get_create_request()

    for point in request['route_points']:
        address = point['address']
        address['coordinates'] = [0, 0]

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Нулевые координаты для клейма',
    }


async def test_create_v2_400_unsupported(taxi_cargo_claims):
    request = utils_v2.get_create_request()

    request['route_points'].append(request['route_points'][0])

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'unsupported_points_count',
        'message': f'Не поддерживается.',
    }


@pytest.mark.parametrize(
    'visit_order, error_message',
    [
        pytest.param(
            [2, 1, 3, 4],
            'source point goes after destination',
            id='source after destination',
        ),
        pytest.param(
            [1, 2, 4, 3],
            'destination point goes after return',
            id='destination after return',
        ),
        pytest.param(
            [4, 1, 2, 3],
            'source point goes after return',
            id='source after return',
        ),
        pytest.param(
            [1, 2, 3, 5],
            'no visit_order #4 in route_points',
            id='missing visit order',
        ),
        pytest.param(
            [1, 2, 2, 3],
            'duplicate visit_order #2 in route_points',
            id='duplicate visit order',
        ),
    ],
)
async def test_create_v2_400_wrong_visit_order_or_point_type(
        taxi_cargo_claims, visit_order, error_message,
):
    request = utils_v2.get_create_request(with_return=True)

    for point, new_visit_order in zip(request['route_points'], visit_order):
        point['visit_order'] = new_visit_order

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': error_message,
    }


@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
        '01234567890123456789012345678912': ['feature_num_1', 'feature_2'],
    },
    CARGO_CLAIMS_FEATURES_VALIDATION_ENABLED=True,
)
async def test_create_features_exist(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request()

    request['features'] = [{'id': 'feature_num_1'}, {'id': 'feature_2'}]

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert sorted(
        response.json()['features'], key=lambda feature: feature['id'],
    ) == sorted(request['features'], key=lambda feature: feature['id'])


@pytest.mark.config(CARGO_CLAIMS_FEATURES_VALIDATION_ENABLED=True)
async def test_create_400_feature_doesnt_exist(taxi_cargo_claims):
    request = utils_v2.get_create_request()

    request['features'] = [{'id': 'feature_num_1'}, {'id': 'feature_2'}]

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Feature doesn\'t exist',
    }


async def test_create_v2_400_wrong_cost(taxi_cargo_claims):
    request = utils_v2.get_create_request()

    request['items'][0]['cost_value'] = ''

    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Некорректное значение цены',
    }


@pytest.mark.parametrize(
    'prefix,api_kind',
    [
        ('/b2b/cargo/integration/', 'api'),
        ('/api/b2b/cargo-claims/', 'corp_client'),
    ],
)
async def test_v2_api_kind(
        taxi_cargo_claims,
        pgsql,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
        prefix,
        api_kind,
):
    headers = get_default_headers()
    headers['X-Cargo-Api-Prefix'] = prefix
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_create_request_v2(),
        headers=headers,
    )

    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT api_kind FROM cargo_claims.claims
        WHERE uuid_id = '{claim_id}'
        """,
    )
    assert list(cursor)[0][0] == api_kind


@pytest.mark.parametrize(
    'prefix,expected_origin_info',
    [
        (
            '/b2b/cargo/integration/',
            {
                'origin': 'api',
                'displayed_origin': 'API',
                'user_agent': 'Yandex',
            },
        ),
        (
            '/api/b2b/cargo-claims/',
            {
                'origin': 'webcorp',
                'displayed_origin': 'Веб',
                'user_agent': 'Yandex',
            },
        ),
    ],
)
async def test_v2_origin_info(
        taxi_cargo_claims,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
        prefix,
        expected_origin_info,
):
    headers = get_default_headers()
    headers['X-Cargo-Api-Prefix'] = prefix
    headers['User-Agent'] = 'Yandex'
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_create_request_v2(),
        headers=headers,
    )
    claim_id = response.json()['id']

    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}', headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()

    assert json['origin_info'] == expected_origin_info


async def test_v2_initiator_yandex_uid(
        taxi_cargo_claims,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
):
    headers = get_default_headers()
    headers['User-Agent'] = 'Yandex'
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_create_request_v2(),
        headers=headers,
    )
    claim_id = response.json()['id']

    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}', headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()

    assert json['initiator_yandex_uid'] == 'user_id'


async def test_v2_create_source(
        taxi_cargo_claims,
        pgsql,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
):
    headers = get_default_headers()
    request_json = get_create_request_v2()
    request_json['referral_source'] = 'bitrix'

    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT referral_source FROM cargo_claims.claims
        WHERE uuid_id = '{claim_id}'
        """,
    )
    assert list(cursor)[0][0] == 'bitrix'


async def test_v2_create_without_return_point(
        taxi_cargo_claims, get_default_headers, get_default_idempotency_token,
):
    headers = get_default_headers()
    request_json = utils_v2.get_create_request(with_return=False)
    request_json['route_points'][0]['external_ref_id'] = 'order_id'

    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    generated_return_point = response.json()['route_points'][-1]
    assert generated_return_point['type'] == 'return'
    assert 'external_ref_id' not in generated_return_point


@pytest.mark.translations(
    cargo={
        'errors.invalid_time_intervals': {
            'en': 'Invalid field time_intervals',
        },
        'key2': {'en': 'fixed'},
    },
)
@pytest.mark.parametrize(
    'config_enabled, expected_response', [(True, 400), (False, 200)],
)
async def test_v2_create_with_invalid_time_intervals(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        config_enabled,
        expected_response,
        taxi_config,
):
    headers = get_default_headers()
    now = datetime.datetime(2020, 9, 1, 8)
    request_json = utils_v2.get_create_request(
        multipoints=True, with_return=True, with_time_intervals=True, now=now,
    )
    taxi_config.set_values(
        dict(CARGO_CLAIMS_TIME_INTERVALS_VALIDATOR_ENABLED=config_enabled),
    )
    request_json['route_points'][0]['external_ref_id'] = 'order_id'
    interval = request_json['route_points'][0]['time_intervals'][0]
    interval['to'], interval['from'] = interval['from'], interval['to']

    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=headers,
    )
    assert response.status_code == expected_response
    if expected_response == 400:
        assert response.json()['message'] == 'Invalid field time_intervals'


@pytest.mark.now('2020-09-01T00:11:00+0300')
async def test_v2_create_with_time_intervals(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    headers = get_default_headers()
    now = datetime.datetime(2020, 9, 1, 8)
    request_json = utils_v2.get_create_request(
        multipoints=True, with_return=True, with_time_intervals=True, now=now,
    )
    request_json['route_points'][0]['external_ref_id'] = 'order_id'

    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    generated_return_point = response.json()['route_points'][-1]
    assert generated_return_point['type'] == 'return'
    assert 'external_ref_id' not in generated_return_point

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT claim_point_id, type, range_from, range_to
        FROM cargo_claims.claim_point_time_intervals
        ORDER BY range_from
        """,
    )
    result = cursor.fetchall()
    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    assert result == [
        (
            1,
            'strict_match',
            datetime.datetime(2020, 9, 1, 11, 10, tzinfo=pg_tz),
            datetime.datetime(2020, 9, 1, 11, 25, tzinfo=pg_tz),
        ),
        (
            2,
            'perfect_match',
            datetime.datetime(2020, 9, 1, 11, 20, tzinfo=pg_tz),
            datetime.datetime(2020, 9, 1, 11, 45, tzinfo=pg_tz),
        ),
        (
            2,
            'strict_match',
            datetime.datetime(2020, 9, 1, 11, 30, tzinfo=pg_tz),
            datetime.datetime(2020, 9, 1, 11, 35, tzinfo=pg_tz),
        ),
    ]


async def test_unknow_zone_id(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    request_json = utils_v2.get_create_request()
    request_json['route_points'][0]['address']['coordinates'] = [1, 1]
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'unknown_zone',
        'message': 'Unknown zone for point A',
    }


async def test_create_with_skip_act(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    request_json = utils_v2.get_create_request()
    request_json['skip_act'] = True
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
    )

    json = response.json()
    assert response.status_code == 200
    assert json['skip_act']

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT skip_act
            FROM cargo_claims.claims
            WHERE uuid_id ='{json['id']}'
        """,
    )
    assert list(cursor)[0][0]


async def test_wrong_pickup_code_usage(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request()
    request['route_points'][0]['pickup_code'] = '123'
    request['route_points'][0]['skip_confirmation'] = True
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'wrong_pickup_code_usage',
        'message': 'Передано поле \'pickup_code\', но при этом смс отключены',
    }


async def test_wrong_pickup_code_format(
        taxi_cargo_claims, get_default_headers,
):
    request = utils_v2.get_create_request()
    request['route_points'][0]['pickup_code'] = 'qwerty123'
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'wrong_pickup_code_format',
        'message': 'Некорректный формат для \'pickup_code\'',
    }


@pytest.mark.parametrize(
    'robot_api_response_code, expected_response_code',
    [
        # Available
        (200, 200),
        # Fallback
        (500, 200),
        # Not available
        (404, 400),
    ],
)
async def test_assign_robot(
        taxi_cargo_claims,
        get_default_headers,
        mock_robot_points_search,
        robot_api_response_code,
        expected_response_code,
):
    mock_robot_points_search.status_code = robot_api_response_code

    request = utils_v2.get_create_request()
    request['client_requirements']['assign_robot'] = True
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == expected_response_code
    if response.status_code == 400:
        assert response.json() == {
            'code': 'validation_error',
            'message': 'Заказы из этой точки нельзя назначать на ровер',
        }


async def test_assign_robot_different_robot_location(
        taxi_cargo_claims,
        get_default_headers,
        get_default_corp_client_id,
        mock_robot_points_search,
):
    mock_robot_points_search.status_code = 200
    mock_robot_points_search.response_body_iter = itertools.cycle(
        ({'location': 1}, {'location': 2}),
    )

    request = utils_v2.get_create_request()
    request['client_requirements']['assign_robot'] = True
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Заказы из этой точки нельзя назначать на ровер',
    }

    requests = [
        sorted(
            mock_robot_points_search.handler.next_call()[
                'request'
            ].query.items(),
        )
        for _ in range(mock_robot_points_search.handler.times_called)
    ]
    expected_requests = [
        # source
        {
            'ext_id': 'cargo:' + get_default_corp_client_id,
            'latitude': '55.800000',
            'longitude': '37.200000',
        }.items(),
        # destination 1
        {'latitude': '55.800000', 'longitude': '37.000000'}.items(),
        # destination 2
        {'latitude': '55.000000', 'longitude': '37.000000'}.items(),
        # return
        {
            'ext_id': 'cargo:' + get_default_corp_client_id,
            'latitude': '55.500000',
            'longitude': '37.000000',
        }.items(),
    ]
    assert sorted(requests) == sorted(map(list, expected_requests))


async def test_create_leave_under_door(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request(leave_under_door=True)
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['route_points'][1]['leave_under_door']


async def test_create_meet_outside(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request(meet_outside=True)
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['route_points'][1]['meet_outside']


async def test_create_no_door_call(taxi_cargo_claims, get_default_headers):
    request = utils_v2.get_create_request(no_door_call=True)
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['route_points'][1]['no_door_call']


@pytest.mark.parametrize('place_id', ['lavka1', 'some_other_place'])
@pytest.mark.parametrize('has_soft_requirements', [True, False])
async def test_create_eats_with_place_id(
        exp_cargo_claims_grocery_shifts,
        taxi_cargo_claims,
        pgsql,
        place_id,
        has_soft_requirements,
):
    soft_requirements = {
        'soft_requirements': [
            {
                'type': 'performer_group',
                'logistic_group': '658',
                'meta_group': 'lavka',
                'performers_restriction_type': 'group_only',
            },
        ],
    }
    request = utils_v2.get_create_request()
    request['custom_context']['place_id'] = place_id
    if has_soft_requirements:
        request['requirements'] = soft_requirements

    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200
    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT dispatch_requirements
            FROM cargo_claims.claims
            WHERE uuid_id ='{claim_id}'
        """,
    )
    dispatch_requirements = list(cursor)[0][0]
    if not has_soft_requirements:
        assert dispatch_requirements is None
    elif place_id == 'lavka1':
        assert dispatch_requirements == {
            'soft_requirements': [
                {
                    'logistic_group': place_id,
                    'shift_type': 'grocery',
                    'type': 'performer_group',
                    'meta_group': 'lavka',
                    'performers_restriction_type': 'group_only',
                },
            ],
        }
    else:
        assert dispatch_requirements == soft_requirements


@pytest.mark.parametrize('place_id', ['lavka1', 'some_other_place'])
async def test_create_eats_with_place_id_and_shift_type_not_patched(
        exp_cargo_claims_grocery_shifts, taxi_cargo_claims, pgsql, place_id,
):
    soft_requirements = {
        'soft_requirements': [
            {
                'type': 'performer_group',
                'logistic_group': '658',
                'meta_group': 'lavka',
                'shift_type': 'eats',
                'performers_restriction_type': 'group_only',
            },
        ],
    }
    request = utils_v2.get_create_request()
    request['custom_context']['place_id'] = place_id
    request['requirements'] = soft_requirements

    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200
    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT dispatch_requirements
            FROM cargo_claims.claims
            WHERE uuid_id ='{claim_id}'
        """,
    )
    dispatch_requirements = list(cursor)[0][0]
    assert dispatch_requirements == soft_requirements


@pytest.mark.parametrize(
    'request_json',
    [
        (
            {
                'emergency_contact': {
                    'name': 'emergency_name',
                    'phone': '+QXYZ8887777',
                },
                'items': utils_v2.get_request_items(),
                'route_points': utils_v2.get_request_points(),
            },
        ),
    ],
)
async def test_wrong_phone_format(
        taxi_cargo_claims,
        taxi_cargo_claims_monitor,
        get_default_headers,
        request_json,
):
    headers = get_default_headers()

    request_id = conftest.get_default_idempotency_token()
    await taxi_cargo_claims.post(
        f'api/integration/v2/claims/create?request_id={request_id}',
        json=request_json,
        headers=headers,
    )

    metrics = await taxi_cargo_claims_monitor.get_metric(
        'invalid-phone-metric',
    )
    assert metrics['country-not-supported'] > 0


@pytest.mark.parametrize(
    'status_filter_enabled, kind_filter_enabled',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_claim_create_event(
        taxi_cargo_claims,
        get_default_headers,
        pgsql,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        status_filter_enabled,
        kind_filter_enabled,
):
    await procaas_claim_status_filter(enabled=status_filter_enabled)
    await procaas_event_kind_filter(enabled=kind_filter_enabled)
    request = utils_v2.get_create_request()
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )
    assert response.status_code == 200

    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT id FROM cargo_claims.processing_events
        WHERE item_id = '{claim_id}'
        """,
    )

    if status_filter_enabled and kind_filter_enabled:
        assert list(cursor) == [(1,)]
    else:
        assert list(cursor) == []


async def test_additional_info_without_client_requirements(
        taxi_cargo_claims, get_default_headers, state_controller, remove_dates,
):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    del request['client_requirements']
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )

    assert claim_info.claim_full_response['origin_info']['origin'] == 'api'
    assert claim_info.claim_full_response['initiator_yandex_uid'] == 'user_id'


async def test_create_modifier_age_check(
        taxi_cargo_claims, get_default_headers,
):
    request = utils_v2.get_create_request(modifier_age_check=True)
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request,
    )

    assert response.status_code == 200

    claim_id = response.json()['id']
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['route_points'][1]['modifier_age_check']


@pytest.mark.parametrize(
    'prefix, status_code, code, message',
    [
        ('/api/b2b/cargo-claims/', 200, None, None),
        (
            '/b2b/cargo/integration/',
            400,
            'sdd_items_without_parameters_forbidden',
            'Грузы без параметров недопустимы',
        ),
    ],
)
async def test_create_sdd_item_params(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        prefix,
        status_code,
        code,
        message,
        get_default_idempotency_token,
        mock_sdd_delivery_intervals,
):
    request = get_create_request_v2()

    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]
    request['items'][0].pop('size')
    request['items'][0].pop('weight')
    request['same_day_data'] = {'delivery_interval': interval}
    del request['client_requirements']

    headers = get_default_headers()
    headers['X-Cargo-Api-Prefix'] = prefix

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == status_code

    if code is not None:
        assert response.json()['code'] == code
    if message is not None:
        assert response.json()['message'] == message


@pytest.mark.parametrize(
    'request_interval, status_code, code, message',
    [
        (
            {
                'from': '2022-02-20T08:10:00+03:00',
                'to': '2022-02-20T12:00:00+03:00',
            },
            200,
            None,
            None,
        ),
        (
            {
                'from': '2022-02-20T08:13:00+03:00',
                'to': '2022-02-20T12:07:00+03:00',
            },
            400,
            'invalid_delivery_interval',
            'Недействительный интервал доставки',
        ),
    ],
)
async def test_create_sdd_diff_timezone(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        mockserver,
        request_interval,
        status_code,
        code,
        message,
):
    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _mock(req):
        return mockserver.make_response(
            status=200,
            json={
                'available_intervals': [
                    {
                        'from': '2022-02-19T19:10:00+00:00',
                        'to': '2022-02-19T22:00:00+00:00',
                    },
                    {
                        'from': '2022-02-20T02:10:00+00:00',
                        'to': '2022-02-20T06:00:00+00:00',
                    },
                    {
                        'from': '2022-02-20T05:10:00+00:00',
                        'to': '2022-02-20T09:00:00+00:00',
                    },
                ],
            },
        )

    request = get_create_request_v2()

    request['same_day_data'] = {'delivery_interval': request_interval}
    del request['client_requirements']

    headers = get_default_headers()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == status_code
    if code is not None:
        assert response.json()['code'] == code
    if message is not None:
        assert response.json()['message'] == message

    assert _mock.times_called == 1


async def test_create_sdd_client_requirements_forbidden(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        mock_sdd_delivery_intervals,
):
    request = get_create_request_v2()

    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]
    request['same_day_data'] = {'delivery_interval': interval}

    headers = get_default_headers()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'sdd_client_requirements_forbidden'
    assert (
        response.json()['message']
        == 'С тарифом "Доставка в течение дня" спецтребования запрещены'
    )


async def test_without_coord(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
        load_json,
):
    yamaps_response = load_json('yamaps_response.json')
    coordinates = yamaps_response['geometry']

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        return [yamaps_response]

    request = get_create_request_v2()
    del request['route_points'][0]['address']['coordinates']

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == 200
    assert (
        response.json()['route_points'][0]['address']['coordinates']
        == coordinates
    )
    for i in range(1, 4):
        assert (
            response.json()['route_points'][i]['address']['coordinates']
            == request['route_points'][i]['address']['coordinates']
        )


async def test_undefined_address(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
):
    request = get_create_request_v2()
    del request['route_points'][0]['address']['coordinates']
    request['route_points'][0]['address']['fullname'] = 'abracadabra'

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


@pytest.mark.parametrize(
    'yamaps_precision, config_precision, code',
    [
        ('NUMBER', 'Number', 200),
        ('RANGE', 'Number', 400),
        ('NUMBER', 'Range', 200),
    ],
)
async def test_geocoder_precision(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
        load_json,
        taxi_config,
        yamaps_precision,
        config_precision,
        code,
):
    taxi_config.set_values(
        {'CARGO_CLAIMS_GEOCODER_PRECISION': {'precision': config_precision}},
    )

    yamaps_response = load_json('yamaps_response.json')
    yamaps_response['geocoder']['precision'] = yamaps_precision

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        return [yamaps_response]

    request = get_create_request_v2()
    del request['route_points'][0]['address']['coordinates']

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == code


@pytest.mark.config(CARGO_CLAIMS_DISABLE_SDD_MULTIPOINTS=True)
async def test_create_sdd_multipoints_disable(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_headers,
        get_default_idempotency_token,
        mock_sdd_delivery_intervals,
):
    request = get_create_request_v2()

    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]
    request['same_day_data'] = {'delivery_interval': interval}
    del request['client_requirements']

    headers = get_default_headers()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'sdd_multipoints_not_supported'
    assert (
        response.json()['message']
        == 'В тарифе "Доставка в течение дня" запрещено'
        ' использовать несколько точек получения'
    )
