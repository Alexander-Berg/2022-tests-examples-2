async def test_apply_changes_comment(
        state_controller, taxi_cargo_claims, get_default_headers,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_comment',
                    'point_id': 1,
                    'comment': 'This is a new comment',
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'applied', change

    claim_info = await state_controller.get_claim_info()
    assert claim_info.claim_full_response['version'] == 2
    for point in claim_info.claim_full_response['route_points']:
        if point['id'] != 1:
            continue
        assert point['address']['comment'] == 'This is a new comment', point


async def test_apply_changes_contact(
        state_controller, get_default_headers, taxi_cargo_claims, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_contact',
                    'point_id': 1,
                    'contact': {
                        'name': 'New contact name',
                        'email': 'new-email@example.com',
                        'phone': '+70001234567',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'applied', change

    claim_info = await state_controller.get_claim_info()
    assert claim_info.claim_full_response['version'] == 2
    for point in claim_info.claim_full_response['route_points']:
        if point['id'] != 1:
            continue
        assert point['contact'] == {
            'name': 'New contact name',
            'personal_email_id': 'new-email@example.com_id',
            'personal_phone_id': '+70001234567_id',
        }, point


async def test_apply_changes_contact_invalid_phone(
        state_controller, get_default_headers, taxi_cargo_claims, mockserver,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_contact',
                    'point_id': 1,
                    'contact': {
                        'name': 'New contact name',
                        'email': 'new-email@example.com',
                        'phone': '+000',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'failed', change
        assert change['error']['code'] == 'country_phone_code_not_supported'


async def test_apply_changes_items(
        state_controller, get_default_headers, taxi_cargo_claims,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    new_items = [
        {
            'title': 'New item title',
            'extra_id': 'New_123',
            'size': {'length': 1.0, 'width': 2.0, 'height': 0.5},
            'cost_value': '100.50',
            'cost_currency': 'RUB',
            'weight': 100.5,
            'pickup_point': 1,
            'droppof_point': 2,
            'quantity': 1,
        },
    ]
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_items',
                    'pickup_point_id': 1,
                    'dropoff_point_id': 2,
                    'items': new_items,
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'applied', change

    claim_info = await state_controller.get_claim_info()
    assert claim_info.claim_full_response['version'] == 2
    items = [
        {k: v for k, v in item.items() if k != 'id'}
        for item in claim_info.claim_full_response['items']
        if item['pickup_point'] == 1 and item['droppof_point'] == 2
    ]
    assert items == new_items


async def test_apply_changes_items_invalid_point(
        state_controller, get_default_headers, taxi_cargo_claims,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    new_items = [
        {
            'title': 'New item title',
            'extra_id': 'New_123',
            'size': {'length': 1.0, 'width': 2.0, 'height': 0.5},
            'cost_value': '100.50',
            'cost_currency': 'RUB',
            'weight': 100.5,
            'pickup_point': 1,
            'droppof_point': 3,
            'quantity': 1,
        },
    ]
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_items',
                    'pickup_point_id': 1,
                    'dropoff_point_id': 2,
                    'items': new_items,
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'failed', change
        assert (
            change['error']['code'] == 'invalid_item_destination_point'
        ), change


async def test_apply_changes_multi(
        state_controller, get_default_headers, taxi_cargo_claims, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_comment',
                    'point_id': 1,
                    'comment': 'This is a new comment',
                },
                {
                    'kind': 'change_contact',
                    'point_id': 1,
                    'contact': {
                        'name': 'New contact name',
                        'email': 'new-email@example.com',
                        'phone': '+70001234567',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200, response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()
    for change in response.json()['changes']:
        assert change['status'] == 'applied', change

    claim_info = await state_controller.get_claim_info()
    assert claim_info.claim_full_response['version'] == 2
