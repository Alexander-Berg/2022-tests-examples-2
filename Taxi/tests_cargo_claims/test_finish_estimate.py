import pytest

from testsuite.utils import matching


async def test_finish_estimate(taxi_cargo_claims, state_controller, load_json):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    request = load_json('finish_estimate_request.json')
    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json=request,
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'ready_for_approval'
    assert response.json()['comment'] == 'Очень полезный комментарий'
    assert response.json()['taxi_offer'] == {
        'offer_id': 'taxi_offer_id_1',
        'price_raw': 999,
        'price': '1198.8012',
    }
    assert response.json()['pricing'] == {
        'offer': {
            'offer_id': 'taxi_offer_id_1',
            'price_raw': 999,
            'price': '1198.8012',
            'valid_until': matching.any_string,
        },
        'currency': 'RUB',
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'руб.',
        },
    }
    assert response.json()['is_delayed'] is False

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': claim_id, 'parts': 'estimation'},
    )
    assert response.json()['taxi_classes_substitution'] == ['express', 'cargo']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_eta_config',
    consumers=['cargo-claims/finish-estimate'],
    clauses=[],
    default_value={'unloading_time': 10},
    is_config=True,
)
@pytest.mark.parametrize(
    'finish_request,expected_eta',
    [
        (
            {
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'taxi_requirements': {'cargo_type': 'gaz'},
                        'items': [{'id': 1, 'quantity': 1}],
                    },
                    {
                        'taxi_class': 'cargo',
                        'items': [{'id': 2, 'quantity': 1}],
                    },
                ],
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'eta': 30,
                'zone_id': 'moscow',
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price_raw': 999,
                    'price': '999.0010',
                },
            },
            50,
        ),
    ],
)
async def test_eta(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        check_zone_id,
        finish_request,
        expected_eta,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}', json=finish_request,
    )

    assert response.status_code == 200

    check_zone_id(claim_id=claim_id)

    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/info' f'?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.json()['eta'] == expected_eta


@pytest.mark.parametrize(
    'request_json',
    [
        {'cars': [], 'failure_reason': 'estimating.sender_blocked'},
        {'cars': [], 'failure_reason': 'estimating.payment_method_cant_order'},
        {'cars': [], 'failure_reason': 'estimating.cant_construct_route'},
        {'cars': [], 'failure_reason': 'estimating.too_large_item'},
        {'cars': [], 'failure_reason': 'estimating.too_large_linear_size'},
        {
            'cars': [],
            'items_comments': [
                {'id': 1, 'comment': 'some comment'},
                {'id': 2, 'comment': 'some comment'},
            ],
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'currency': 'RUB',
        },
    ],
)
async def test_no_cars_found(
        taxi_cargo_claims, state_controller, get_default_headers, request_json,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}',
        json=request_json,
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'estimating_failed'


async def test_overwrite_old_estimation(
        taxi_cargo_claims, state_controller, get_claim,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}',
        json={
            'cars': [],
            'failure_reason': 'estimating.required_tariffs_forbidden',
        },
    )
    assert response.status_code == 200

    response = await get_claim(claim_id)
    assert response['status'] == 'estimating_failed'
    assert response['error_messages'] == [
        {
            'code': 'estimating.required_tariffs_forbidden',
            'message': 'Не удалось подобрать машину для данной заявки',
        },
    ]

    for _ in range(2):
        response = await taxi_cargo_claims.post(
            f'v1/claims/finish-estimate?claim_id={claim_id}',
            json={'cars': [], 'failure_reason': 'estimating.too_large_item'},
        )
        assert response.status_code == 200

        response = await get_claim(claim_id)
        assert response['status'] == 'estimating_failed'
        assert response['error_messages'] == [
            {
                'code': 'estimating.too_large_item',
                'message': (
                    'Слишком габаритные товары: суммарный объем '
                    'товаров превышает вместимость транспортного средства.'
                ),
            },
        ]


async def test_client_requirements_warning(
        taxi_cargo_claims, state_controller, get_internal_claim_response,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    estimate_response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json={
            'cars': [
                {
                    'taxi_class': 'cargo',
                    'taxi_requirements': {'cargo_type': 'gaz'},
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'currency': 'RUB',
            'warnings': [
                {
                    'source': 'client_requirements',
                    'code': 'not_fit_in_car',
                    'details_code': 'estimating.warning.too_large_item',
                    'details_args': {'item_title': 'холодильник'},
                },
            ],
            'zone_id': 'moscow',
        },
    )
    assert estimate_response.status_code == 200

    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    json = response.json()
    assert json['status'] == 'ready_for_approval'
    assert json['warnings'] == [
        {
            'source': 'client_requirements',
            'code': 'not_fit_in_car',
            'message': (
                'холодильник имеет слишком большие габариты'
                ' и может не поместиться'
            ),
        },
    ]


async def test_door_to_door(taxi_cargo_claims, state_controller, get_claim):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate?claim_id=%s' % claim_id,
        json={
            'cars': [
                {
                    'taxi_class': 'express',
                    'taxi_requirements': {'door_to_door': True},
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'zone_id': 'moscow',
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
                'currency_code': 'RUB',
            },
        },
    )
    assert response.status_code == 200

    response = await get_claim(claim_id)
    assert response['status'] == 'ready_for_approval'
    assert response['matched_cars'] == [
        {'door_to_door': True, 'taxi_class': 'express'},
    ]


async def test_pro_courier(taxi_cargo_claims, state_controller, get_claim):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate?claim_id=%s' % claim_id,
        json={
            'cars': [
                {
                    'taxi_class': 'express',
                    'taxi_requirements': {'pro_courier': True},
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'zone_id': 'moscow',
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
                'currency_code': 'RUB',
            },
        },
    )
    assert response.status_code == 200

    response = await get_claim(claim_id)
    assert response['status'] == 'ready_for_approval'
    assert response['matched_cars'] == [
        {'pro_courier': True, 'taxi_class': 'express'},
    ]


@pytest.mark.parametrize('tariff', ['cargocorp', 'express'])
async def test_cargo_points(
        taxi_cargo_claims, state_controller, get_claim, tariff,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate?claim_id=%s' % claim_id,
        json={
            'zone_id': 'moscow',
            'cars': [
                {
                    'taxi_class': tariff,
                    'taxi_requirements': {
                        'cargo_points': [2, 2, 2, 2, 2],
                        'cargo_points_field': f'fake_middle_point_{tariff}',
                    },
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.10',
                'currency_code': 'RUB',
            },
        },
    )
    assert response.status_code == 200

    response = await get_claim(claim_id)
    assert response['matched_cars'] == [
        {
            'cargo_points': [2, 2, 2, 2, 2],
            'cargo_points_field': f'fake_middle_point_{tariff}',
            'taxi_class': tariff,
        },
    ]


async def test_client_taxi_class(
        taxi_cargo_claims, state_controller, get_claim,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate?claim_id=%s' % claim_id,
        json={
            'zone_id': 'moscow',
            'cars': [
                {
                    'taxi_class': 'cargocorp',
                    'client_taxi_class': 'cargo',
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.10',
                'currency_code': 'RUB',
            },
        },
    )
    assert response.status_code == 200

    response = await get_claim(claim_id)
    assert response['matched_cars'] == [{'taxi_class': 'cargo'}]


@pytest.mark.config(
    CARGO_TYPE_LIMITS={
        'lcv_m': {
            'requirement_value': 2,
            'height_min_cm': 1,
            'height_max_cm': 1,
            'width_min_cm': 1,
            'width_max_cm': 1,
            'length_min_cm': 1,
            'length_max_cm': 1,
            'carrying_capacity_min_kg': 1,
            'carrying_capacity_max_kg': 1,
        },
    },
)
async def test_cargo_type_int(taxi_cargo_claims, state_controller):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}',
        json={
            'cars': [
                {
                    'taxi_class': 'cargo',
                    'taxi_requirements': {'cargo_type_int': 2},
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'zone_id': 'moscow',
            'currency': 'RUB',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'is_delayed': False,
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.get(
        f'/v2/claims/full?claim_id={claim_id}',
    )
    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json['matched_cars'][0]['cargo_type'] == 'lcv_m'
    assert resp_json['matched_cars'][0]['cargo_type_int'] == 2
    assert resp_json['taxi_requirements'] == {'cargo_type_int': 2}


async def test_finish_estimate_offer_ttl(
        taxi_cargo_claims, state_controller, get_default_headers, mocked_time,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json={
            'cars': [
                {
                    'taxi_class': 'cargo',
                    'taxi_requirements': {'cargo_type': 'gaz'},
                    'items': [{'id': 1, 'quantity': 1}],
                },
                {'taxi_class': 'cargo', 'items': [{'id': 2, 'quantity': 1}]},
            ],
            'zone_id': 'moscow',
            'currency': 'RUB',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'is_delayed': False,
            'taxi_classes_substitution': ['express', 'cargo'],
            'offer_ttl': 10,
        },
    )
    assert response.status_code == 200

    mocked_time.sleep(1000)
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/accept',
        params={'claim_id': claim_id},
        json={'version': 1},
        headers=get_default_headers(),
    )
    assert response.status_code == 409


async def test_finish_estimate_from_status_new(
        taxi_cargo_claims, state_controller, get_default_headers, mocked_time,
):
    claim_info = await state_controller.apply(target_status='new')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json={
            'cars': [
                {
                    'taxi_class': 'cargo',
                    'taxi_requirements': {'cargo_type': 'gaz'},
                    'items': [{'id': 1, 'quantity': 1}],
                },
                {'taxi_class': 'cargo', 'items': [{'id': 2, 'quantity': 1}]},
            ],
            'zone_id': 'moscow',
            'currency': 'RUB',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'is_delayed': False,
            'taxi_classes_substitution': ['express', 'cargo'],
            'offer_ttl': 10,
        },
    )
    assert response.status_code == 200


async def test_failure_message(
        taxi_cargo_claims, state_controller, get_default_headers, mocked_time,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    request_json = {
        'cars': [],
        'failure_reason': 'estimating.cargocorp_payment_failure',
        'failure_message': 'Debt',
    }
    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}',
        json=request_json,
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'estimating_failed'
    assert new_claim_info.claim_full_response['error_messages'] == [
        {'code': 'estimating.cargocorp_payment_failure', 'message': 'Debt'},
    ]
