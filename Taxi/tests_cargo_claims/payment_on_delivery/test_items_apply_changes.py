import pytest

NEW_ITEMS = [
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
        'fiscalization': {
            'item_type': 'product',
            'article': '20ML50OWKY4FC86',
            'nds': 'vat_10',
            'supplier_inn': '3664069397',
        },
    },
]


def _make_items(count_at_point=1):
    items = []
    for dropoff_point_id in range(2, 4):
        for i in range(count_at_point):
            items.append(
                {
                    'title': f'title {dropoff_point_id}/{i}',
                    'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                    'cost_value': '10.40',
                    'cost_currency': 'RUB',
                    'weight': 10.2,
                    'pickup_point': 1,
                    'droppof_point': dropoff_point_id,
                    'quantity': 2,
                },
            )
    return items


@pytest.mark.parametrize(
    'request_status, change_status', [(200, 'applied'), (409, 'failed')],
)
async def test_apply_changes_items(
        mockserver,
        taxi_cargo_claims,
        get_default_headers,
        create_segment_with_payment,
        mock_payment_validate,
        mock_payment_create,
        request_status,
        change_status,
):
    @mockserver.json_handler('/cargo-payments/v1/payment/update')
    def _payment_update(request):
        return mockserver.make_response(json={}, status=request_status)

    claim_info = await create_segment_with_payment(payment_method='card')

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
                    'items': NEW_ITEMS,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert _payment_update.times_called == 1

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id, 'request_id': '123456'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200, response.json()

    for change in response.json()['changes']:
        assert change['status'] == change_status


async def test_apply_changes_items_support_ok(
        mockserver,
        taxi_cargo_claims,
        get_apply_changes_headers,
        get_default_headers,
        create_segment_with_payment,
        mock_payment_validate,
        mock_payment_create,
):
    @mockserver.json_handler('/cargo-payments/v1/payment/update')
    def _payment_update(request):
        return mockserver.make_response(json={}, status=200)

    claim_info = await create_segment_with_payment(payment_method='card')

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/apply-changes/request',
        params={'claim_id': claim_info.claim_id},
        headers=get_apply_changes_headers(get_default_headers),
        json={
            'last_known_revision': '1',
            'changes': [
                {
                    'kind': 'change_items',
                    'pickup_point_id': 1,
                    'dropoff_point_id': 2,
                    'items': NEW_ITEMS,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert _payment_update.times_called == 1

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/apply-changes/result',
        params={'claim_id': claim_info.claim_id},
        headers=get_apply_changes_headers(get_default_headers),
    )
    assert response.status_code == 200, response.json()

    for change in response.json()['changes']:
        assert change['status'] == 'applied'


def _get_items_from_claim(claim_info, pickup_point_id=1, dropoff_point_id=2):
    items_for_point = []
    for item in claim_info.claim_full_response['items']:
        if item['pickup_point'] != pickup_point_id:
            continue
        if item['droppof_point'] != dropoff_point_id:
            continue
        items_for_point.append(item.copy())

    return items_for_point


@pytest.fixture(name='request_apply_changes')
async def _request_apply_changes(
        taxi_cargo_claims, get_apply_changes_headers, get_default_headers,
):
    async def wrapper(claim_id, changes):
        return await taxi_cargo_claims.post(
            '/v2/admin/claims/apply-changes/request',
            params={'claim_id': claim_id},
            headers=get_apply_changes_headers(get_default_headers),
            json={'last_known_revision': '1', 'changes': changes},
        )

    return wrapper


@pytest.fixture(name='result_apply_changes')
async def _result_apply_changes(
        taxi_cargo_claims, get_apply_changes_headers, get_default_headers,
):
    async def wrapper(claim_id):
        response = await taxi_cargo_claims.post(
            '/v2/admin/claims/apply-changes/result',
            params={'claim_id': claim_id},
            headers=get_apply_changes_headers(get_default_headers),
        )
        assert response.status_code == 200, response.json()
        return response.json()['changes']

    return wrapper


@pytest.fixture(name='request_items_changes')
async def _request_items_changes(request_apply_changes):
    async def wrapper(*, claim_id=None, claim_info=None, items=None):
        if items is None:
            items = _get_items_from_claim(claim_info)
            claim_id = claim_info.claim_id

        changes = [
            {
                'kind': 'change_items',
                'pickup_point_id': 1,
                'dropoff_point_id': 2,
                'items': items,
            },
        ]
        return await request_apply_changes(claim_id, changes=changes)

    return wrapper


async def test_apply_changes_items_support_failed(
        request_items_changes,
        result_apply_changes,
        create_segment_with_payment,
        mock_payment_validate,
        mock_payment_create,
        mock_payment_update,
        error_message='pass as is from cargo-payments',
):
    mock_payment_update.status_code = 410
    mock_payment_update.error_message = error_message

    claim_info = await create_segment_with_payment(payment_method='card')

    response = await request_items_changes(claim_info=claim_info)

    assert response.status_code == 200
    assert mock_payment_update.handler.times_called == 1

    changes = await result_apply_changes(claim_id=claim_info.claim_id)

    assert changes == [
        {
            'error': {
                'code': 'cargo_payments_update_error',
                'details': error_message,
                'message': 'Can not change payment on delivery parameters',
            },
            'id': 1,
            'kind': 'change_items',
            'status': 'failed',
        },
    ]


async def test_apply_changes_items_post_payment(
        request_items_changes,
        result_apply_changes,
        create_segment_with_payment,
        mock_payment_validate,
        mock_payment_create,
        mock_payment_update,
):
    claim_info = await create_segment_with_payment(payment_method='card')

    response = await request_items_changes(claim_info=claim_info)

    assert response.status_code == 200
    assert mock_payment_update.handler.times_called == 1

    changes = await result_apply_changes(claim_id=claim_info.claim_id)

    assert changes == [{'id': 1, 'kind': 'change_items', 'status': 'applied'}]


async def test_items_quantity_change_ok(
        request_items_changes,
        result_apply_changes,
        create_segment_with_performer,
        mock_payment_validate,
        mock_payment_create,
        mock_payment_update,
        do_prepare_segment_state,
):
    """
        Check items change after pickup allowed
        with skip_confirmation.
    """

    segment = await create_segment_with_performer(
        payment_method='card', skip_confirmation=True,
    )
    await do_prepare_segment_state(
        segment, visit_order=2, last_exchange_init=False,
    )
    # pickuped

    new_items = _get_items_from_claim(segment.claim_info)
    new_items[0]['quantity'] += 11

    response = await request_items_changes(
        claim_id=segment.claim_id, items=new_items,
    )

    assert response.status_code == 200
    assert mock_payment_update.handler.times_called == 1

    changes = await result_apply_changes(claim_id=segment.claim_id)

    assert changes == [{'id': 1, 'kind': 'change_items', 'status': 'applied'}]


@pytest.mark.parametrize(
    'change_kind,error_details',
    [
        (
            'remove_old',
            'Change items quantity after confirmation with sms is not allowed'
            ', old unique item titles 2, new unique item titles 1',
        ),
        (
            'add_new',
            'Change items quantity after confirmation with sms is not allowed'
            ', old unique item titles 2, new unique item titles 3',
        ),
        (
            'change_quantity',
            'Change items quantity after confirmation with sms is not allowed'
            ', for item \'item title 1\' old quantity 3, new quantity 4',
        ),
        (
            'rename_title',
            'Change items quantity after confirmation with sms is not allowed'
            ', missing old item \'some new title\'',
        ),
    ],
)
async def test_items_quantity_change_prohibited(
        request_items_changes,
        result_apply_changes,
        create_segment_with_performer,
        do_prepare_segment_state,
        change_kind: str,
        error_details: str,
):
    """
        Check items change after pickup allowed
        with skip_confirmation.
    """

    segment = await create_segment_with_performer(
        skip_confirmation=False, custom_items=_make_items(count_at_point=2),
    )
    await do_prepare_segment_state(
        segment, visit_order=2, last_exchange_init=False,
    )
    # pickuped

    new_items = _get_items_from_claim(segment.claim_info)
    if change_kind == 'remove_old':
        new_items = new_items[1:]
    elif change_kind == 'add_new':
        new_item = new_items[-1].copy()
        new_item['title'] = 'some new title'
        new_items.append(new_item)
    elif change_kind == 'change_quantity':
        new_items[0]['quantity'] += 1
    elif change_kind == 'rename_title':
        new_items[0]['title'] = 'some new title'

    response = await request_items_changes(
        claim_id=segment.claim_id, items=new_items,
    )

    assert response.status_code == 200

    changes = await result_apply_changes(claim_id=segment.claim_id)

    assert changes == [
        {
            'error': {
                'code': 'not_allowed',
                'details': error_details,
                'message': 'Refresh the page',
            },
            'id': 1,
            'kind': 'change_items',
            'status': 'failed',
        },
    ]
