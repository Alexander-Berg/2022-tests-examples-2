import pytest


async def test_get_not_found(taxi_cargo_claims, get_default_headers):
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info?claim_id=some_not_found',
        headers=get_default_headers(),
    )
    assert response.status_code == 404


# test should return 400, because method forbidden,
# except corp_clients from config
# CARGO_CLAIMS_COPR_CLIENTS_LIST_ALLOWED_TO_USE_V1
async def test_bad_corp_client(taxi_cargo_claims, get_default_headers):
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info?claim_id=12345',
        headers=get_default_headers('other_corp_id0123456789012345678'),
    )
    assert response.status_code == 400


async def test_get(
        taxi_cargo_claims,
        get_default_corp_claim_response,
        get_default_headers,
        state_controller,
        remove_dates,
):
    claim_info = await state_controller.apply(target_status='new')
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers(),
    )
    expected_response = get_default_corp_claim_response(claim_info.claim_id)
    assert response.status_code == 200
    json = response.json()
    remove_dates(json)
    assert json == expected_response

    # Update claim
    await state_controller.apply(
        target_status='ready_for_approval', fresh_claim=False,
    )
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/info?claim_id=%s' % claim_info.claim_id,
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    json = response.json()
    assert json['matched_cars'] == [
        {'taxi_class': 'cargo', 'cargo_loaders': 2, 'cargo_type': 'lcv_m'},
    ]
    assert json['status'] == 'ready_for_approval'


@pytest.mark.parametrize(
    'db_error_reason,error_message,error_code',
    [
        pytest.param(
            'estimating.too_large_item',
            'Слишком габаритные товары: суммарный объем товаров'
            ' превышает вместимость транспортного средства.',
            'estimating.too_large_item',
            id='too_large_item',
        ),
        pytest.param(
            # case with reason missed in tanker
            'estimating.too_many_loaders',
            'Не удалось подобрать машину для данной заявки',
            'estimating.too_many_loaders',
            id='too_many_loaders',
        ),
        pytest.param(
            # case without reason in db
            '',
            'Не удалось подобрать машину для данной заявки',
            'errors.default_estimating_failed',
            id='default_estimating_failed',
        ),
    ],
)
async def test_get_with_errors(
        taxi_cargo_claims,
        get_default_corp_claim_response,
        get_default_headers,
        state_controller,
        db_error_reason,
        error_message,
        error_code,
        remove_dates,
):
    claim_info = await state_controller.apply(target_status='estimating')

    req_json = {'cars': []}
    if db_error_reason:
        req_json['failure_reason'] = db_error_reason

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_info.claim_id}',
        json=req_json,
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info?claim_id=%s' % claim_info.claim_id,
        headers=get_default_headers(),
    )

    expected_response = get_default_corp_claim_response(claim_info.claim_id)
    expected_response['status'] = 'estimating_failed'
    expected_response['error_messages'] = [
        {'code': error_code, 'message': error_message},
    ]

    assert response.status_code == 200
    json = response.json()
    remove_dates(json)
    assert json == expected_response


async def test_get_with_taxi_order_errors(
        taxi_cargo_claims,
        state_controller,
        get_default_corp_claim_response,
        get_default_headers,
        remove_dates,
        get_segment_id,
        build_segment_update_request,
):
    claim_info = await state_controller.apply(target_status='performer_draft')
    claim_id = claim_info.claim_id

    segment_id = await get_segment_id()
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id=None,
                    with_order=False,
                    with_performer=False,
                    resolution='performer_not_found',
                    revision=5,
                ),
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info?claim_id=%s' % claim_id,
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    expected_response = get_default_corp_claim_response(
        claim_id, with_offer=True,
    )
    expected_response['status'] = 'performer_not_found'
    del expected_response['available_cancel_state']
    expected_response['error_messages'] = [
        {
            'code': 'errors.default_performer_not_found',
            'message': 'Не удалось найти исполнителя на заявку',
        },
    ]

    json = response.json()
    remove_dates(json)
    assert json == expected_response


async def test_performer_info_doesnt_exist_when_not_found(
        taxi_cargo_claims, get_default_headers, state_controller,
):
    claim_info = await state_controller.apply(target_status='new')

    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert 'performer_info' not in response.json()


async def test_found_performer_info(
        taxi_cargo_claims, get_default_headers, state_controller,
):
    claim_info = await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['performer_info'] == {
        'courier_name': 'Kostya',
        'legal_name': 'park_org_name_1',
        'car_model': 'car_model_1',
        'car_number': 'car_number_1',
        'car_color': '-',
        'car_color_hex': '-',
        'transport_type': '-',
    }


@pytest.mark.parametrize('optional_return', [False, True])
async def test_cancel_state_with_optional_return(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        optional_return,
):
    state_controller.set_options(optional_return=optional_return)
    claim_info = await state_controller.apply(target_status='pickuped')

    # optional_return == False
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    if optional_return:
        assert response.json()['available_cancel_state'] == 'paid'
    else:
        assert not response.json().get('available_cancel_state')
