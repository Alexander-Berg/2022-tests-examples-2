async def test_exchange_act_simple(taxi_cargo_claims, state_controller):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(
        target_status='delivery_arrived', next_point_order=2,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={'claim_id': claim_info.claim_id, 'point_id': 2},
        json={
            'items': [{'extra_id': '1', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    claim_info = await state_controller.apply(
        target_status='pickuped', next_point_order=3, fresh_claim=False,
    )

    point = claim_info.get_point_by_id(2)
    assert point.visit_status == 'partial_delivery'

    for item in claim_info.claim_full_response['items']:
        if item['extra_id'] == '1':
            assert item['delivered_quantity'] == 1, item
        elif item['droppof_point'] == 2:
            assert item['delivered_quantity'] == 0, item


async def test_exchange_act_last_point(taxi_cargo_claims, state_controller):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(
        target_status='delivery_arrived', next_point_order=3,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={'claim_id': claim_info.claim_id, 'point_id': 3},
        json={
            'items': [{'extra_id': '2', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    claim_info = await state_controller.apply(
        target_status='delivered', next_point_order=4, fresh_claim=False,
    )

    assert claim_info.current_state.status == 'returning'

    point = claim_info.get_point_by_id(3)
    assert point.visit_status == 'partial_delivery'


async def test_exchange_act_zero_quantities(
        taxi_cargo_claims, state_controller,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(
        target_status='delivery_arrived', next_point_order=3,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={'claim_id': claim_info.claim_id, 'point_id': 3},
        json={
            'items': [{'extra_id': '2', 'quantity': 0}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    claim_info = await state_controller.apply(
        target_status='delivered', next_point_order=4, fresh_claim=False,
    )

    assert claim_info.current_state.status == 'returning'

    point = claim_info.get_point_by_id(3)
    assert point.visit_status == 'partial_delivery'

    for item in claim_info.claim_full_response['items']:
        if item['droppof_point'] == 3:
            assert item['delivered_quantity'] == 0, item
