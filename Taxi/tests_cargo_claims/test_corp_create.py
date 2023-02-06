import copy
import datetime
import itertools
import uuid

import pytest


async def test_create(
        taxi_cargo_claims,
        claim_creator,
        get_default_headers,
        get_default_corp_claim_response,
        clear_event_times,
        remove_dates,
        pgsql,
):
    response = await claim_creator()

    assert response.status_code == 200
    json = response.json()
    assert json['created_ts'] != '1970-01-01T00:00:00+00:00'
    assert json['updated_ts'] != '1970-01-01T00:00:00+00:00'
    clear_event_times(json)
    assert json == get_default_corp_claim_response(response.json()['id'])

    # test double request
    response = await claim_creator()
    assert response.status_code == 200

    json = response.json()
    remove_dates(json)
    assert json == get_default_corp_claim_response(json['id'])

    # test double request with other client id
    response = await claim_creator(
        headers=get_default_headers('01234567890123456789012345678999'),
    )

    assert response.status_code == 200
    json = response.json()
    remove_dates(json)
    expected_json = get_default_corp_claim_response(response.json()['id'])
    expected_json['corp_client_id'] = '01234567890123456789012345678999'

    assert json == expected_json

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
    SELECT yandex_login FROM cargo_claims.claims
        """,
    )
    assert list(cursor) == [('abacaba',), ('abacaba',)]


async def test_create_client_requirements(
        taxi_cargo_claims,
        claim_creator,
        get_default_request,
        get_default_headers,
):
    client_requirements = {
        'taxi_class': 'cargo',
        'cargo_type': 'van',
        'cargo_loaders': 3,
        'cargo_options': ['thermal_bag'],
        'pro_courier': True,
        'extra_requirement': 22,
    }

    response = await claim_creator(
        request={
            **get_default_request(),
            'client_requirements': client_requirements,
        },
    )
    claim_id = response.json()['id']

    assert response.status_code == 200
    assert response.json()['client_requirements'] == client_requirements

    # test search client_requirements
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/search',
        json={'offset': 0, 'limit': 1},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert (
        response.json()['claims'][0]['client_requirements']
        == client_requirements
    )

    # test info client_requirements
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/info?claim_id={claim_id}',
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['client_requirements'] == client_requirements

    # test admin full
    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['claim']['client_requirements'] == client_requirements
    )

    # test full
    response = await taxi_cargo_claims.get(
        f'/v2/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200
    assert response.json()['client_requirements'] == client_requirements


async def test_create_client_requirements_no_weights(
        taxi_cargo_claims,
        claim_creator,
        get_default_request,
        get_default_headers,
):
    client_requirements = {
        'taxi_class': 'cargo',
        'cargo_type': 'van',
        'cargo_loaders': 3,
    }

    request = get_default_request()
    request['client_requirements'] = client_requirements

    request['items'][0].pop('size')
    request['items'][0].pop('weight')

    response = await claim_creator(request=request)
    assert response.status_code == 200
    claim_id = response.json()['id']

    del request['client_requirements']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create?request_id={claim_id}',
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'items_without_parameters_forbidden',
        'message': (
            'Грузы без параметров недопустимы, '
            'если отсутствуют требования на тип машины'
        ),
    }


async def test_creation_sharing_key(
        taxi_cargo_claims, get_sharing_keys, create_default_claim,
):
    sharing_key = get_sharing_keys(claim_uuid=create_default_claim.claim_id)[0]

    assert uuid.UUID(sharing_key)


@pytest.mark.parametrize(
    'callback_url, expected_response_code',
    [
        ('https://www.example.com/?my_order_id=123&', 200),
        ('http://www.example.com/?my_order_id=123&', 200),
        ('ftp://ftp.example.com/?', 400),
        ('mongo://localhost/?', 400),
    ],
)
async def test_callback_url_validation(
        taxi_cargo_claims,
        claim_creator,
        get_default_request,
        callback_url,
        expected_response_code,
):
    request_data = copy.deepcopy(get_default_request())
    request_data['callback_properties'] = {'callback_url': callback_url}

    response = await claim_creator(request=request_data)
    assert response.status_code == expected_response_code


@pytest.mark.parametrize(
    'delta',
    [
        datetime.timedelta(minutes=-5),
        datetime.timedelta(minutes=5),
        datetime.timedelta(days=2),
    ],
)
async def test_any_due_accepted(
        claim_creator,
        get_default_request,
        now,
        delta,
        get_claim,
        to_iso8601,
        from_iso8601,
        close_datetimes,
):
    request_data = copy.deepcopy(get_default_request())
    due = now + delta
    request_data['due'] = to_iso8601(now + delta)

    response = await claim_creator(request=request_data)
    assert response.status_code == 200

    claim = await get_claim(response.json()['id'])
    new_due = from_iso8601(claim['due'])

    assert close_datetimes(due, new_due)


@pytest.mark.parametrize(
    'option_name',
    [
        'skip_client_notify',
        'skip_emergency_notify',
        'optional_return',
        'skip_door_to_door',
    ],
)
async def test_create_with_skip_options(
        taxi_cargo_claims, claim_creator, get_default_request, option_name,
):

    request_data = copy.deepcopy(get_default_request())
    request_data[option_name] = True

    response = await claim_creator(request=request_data)

    assert response.status_code == 200
    assert response.json()[option_name]


async def test_return_point_was_add(claim_creator, get_default_request):
    request = get_default_request()
    request['route_points'] = {
        'source': {
            'address': {
                'fullname': 'БЦ Аврора',
                'coordinates': [37.5, 55.7],
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Садовническая улица',
                'building': '82',
                'porch': '4',
            },
            'contact': {
                'phone': '+71111111111',
                'name': 'string',
                'email': 'source@yandex.ru',
            },
        },
        'destination': {
            'address': {
                'fullname': 'Свободы, 30',
                'coordinates': [37.6, 55.6],
                'country': 'Украина',
                'city': 'Киев',
                'street': 'Свободы',
                'building': '30',
                'porch': '2',
                'floor': 12,
                'flat': 87,
                'door_code': '0к123',
                'comment': 'other_comment',
            },
            'contact': {
                'phone': '+72222222222',
                'name': 'string',
                'phone_additional_code': '123 45 678',
            },
        },
    }

    response = await claim_creator(request=request)
    assert response.status_code == 200
    assert (
        response.json()['route_points']['return']['contact']['phone']
        == '+71111111111'
    )
    assert (
        response.json()['route_points']['source']['contact']['phone']
        == '+71111111111'
    )
    assert (
        response.json()['route_points']['destination']['contact']['phone']
        == '+72222222222'
    )


async def test_string_floor_and_flat(claim_creator, get_default_request):
    request = get_default_request()
    del request['route_points']['destination']['address']['flat']
    del request['route_points']['destination']['address']['floor']

    request['route_points']['destination']['address']['sfloor'] = 'new_sfoor'
    request['route_points']['destination']['address']['sflat'] = 'new_sflat'

    response = await claim_creator(request=request)
    assert response.status_code == 200

    destination_address = response.json()['route_points']['destination'][
        'address'
    ]
    assert destination_address['sfloor'] == 'new_sfoor'
    assert destination_address['sflat'] == 'new_sflat'

    assert 'flat' not in destination_address
    assert 'floor' not in destination_address


async def test_complex_context(claim_creator, get_default_request):
    request = get_default_request()
    request['custom_context'] = {'key': {'some': 123}}
    response = await claim_creator(request=request)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'prefix,api_kind',
    [
        ('/b2b/cargo/integration/', 'api'),
        ('/api/b2b/cargo-claims/', 'corp_client'),
    ],
)
async def test_api_kind(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
        prefix,
        api_kind,
):
    headers = get_default_headers()
    headers['X-Cargo-Api-Prefix'] = prefix
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_default_request(),
        headers=headers,
    )

    json = response.json()
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT api_kind
            FROM cargo_claims.claims
            WHERE uuid_id ='{json['id']}'
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
async def test_origin_info(
        taxi_cargo_claims,
        get_default_headers,
        get_default_request,
        get_default_idempotency_token,
        prefix,
        expected_origin_info,
):
    headers = get_default_headers()
    headers['X-Cargo-Api-Prefix'] = prefix
    headers['User-Agent'] = 'Yandex'
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_default_request(),
        headers=headers,
    )
    json = response.json()
    claim_id = json['id']

    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}', headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()

    assert json['origin_info'] == expected_origin_info


async def test_initiator_yandex_uid(
        taxi_cargo_claims,
        get_default_headers,
        get_default_request,
        get_default_idempotency_token,
):
    headers = get_default_headers()
    headers['User-Agent'] = 'Yandex'
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_default_request(),
        headers=headers,
    )
    json = response.json()
    claim_id = json['id']

    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}', headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()

    assert json['initiator_yandex_uid'] == 'user_id'


@pytest.mark.config(CARGO_CLAIMS_ACT_COUNTRY_LIST=[])
async def test_create_skip_act(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_default_request(),
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


async def test_create_referral_source(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    request_json = get_default_request()
    request_json['referral_source'] = 'bitrix'
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
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


async def test_dispatch_flow_newway(
        state_controller,
        get_default_corp_client_id,
        get_db_segment_ids,
        create_segment_for_claim,
):
    claim_info = await state_controller.apply(target_status='accepted')
    await create_segment_for_claim(claim_info.claim_id)
    created_segments = await get_db_segment_ids()
    assert len(created_segments) == 1


async def test_create_v1_zero_lon_and_lat(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
):
    request_json = get_default_request()
    request_json['route_points']['source']['address']['coordinates'] = [0, 0]
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Нулевые координаты для клейма',
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
        get_default_request,
        get_default_idempotency_token,
        robot_api_response_code,
        expected_response_code,
):
    mock_robot_points_search.status_code = robot_api_response_code

    request_json = get_default_request()
    request_json['client_requirements']['assign_robot'] = True
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
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
        mock_robot_points_search,
        get_default_request,
        get_default_idempotency_token,
        get_default_corp_client_id,
):
    mock_robot_points_search.status_code = 200
    mock_robot_points_search.response_body_iter = itertools.cycle(
        ({'location': 1}, {'location': 2}),
    )

    request_json = get_default_request()
    request_json['client_requirements']['assign_robot'] = True
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=request_json,
        headers=get_default_headers(),
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
            'latitude': '55.700000',
            'longitude': '37.500000',
        }.items(),
        # destination
        {'latitude': '55.600000', 'longitude': '37.600000'}.items(),
    ]
    assert sorted(requests) == sorted(map(list, expected_requests))


async def test_without_coord(
        taxi_cargo_claims,
        get_default_request,
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

    request = get_default_request()
    del request['route_points']['destination']['address']['coordinates']

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
        json=request,
        headers=headers,
        params={'request_id': get_default_idempotency_token},
    )

    assert response.status_code == 200
    assert (
        response.json()['route_points']['source']['address']['coordinates']
        == request['route_points']['source']['address']['coordinates']
    )
    assert (
        response.json()['route_points']['destination']['address'][
            'coordinates'
        ]
        == coordinates
    )


async def test_undefined_address(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
):
    request = get_default_request()
    del request['route_points']['destination']['address']['coordinates']
    request['route_points']['destination']['address'][
        'fullname'
    ] = 'abracadabra'

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/create',
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
