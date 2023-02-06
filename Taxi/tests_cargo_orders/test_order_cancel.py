import pytest


@pytest.fixture(name='mock_intapi_orders_cancel')
def _mock_intapi_orders_cancel(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200

    context = Context()

    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            json={'message': f'failed with code {context.status_code}'},
            status=context.status_code,
        )

    return context


@pytest.mark.parametrize('cancel_state', ['free', 'paid'])
async def test_order_cancel(
        taxi_cargo_orders,
        mock_intapi_orders_cancel,
        default_order_id,
        cancel_state: str,
):
    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': cancel_state,
            'dispatch_version': 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {'cancel_state': cancel_state}


@pytest.mark.pgsql(
    'cargo_orders', files=['state_single_order_wo_provider_id.sql'],
)
async def test_bad_no_provider_id(
        taxi_cargo_orders, mock_intapi_orders_cancel, default_order_id,
):
    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    'provider_status_code, expecting_code', [(404, 404), (409, 409)],
)
async def test_bad_provider_cancel_error(
        taxi_cargo_orders,
        mock_intapi_orders_cancel,
        default_order_id,
        provider_status_code: int,
        expecting_code: int,
):
    mock_intapi_orders_cancel.status_code = provider_status_code

    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
        },
    )

    assert response.status_code == expecting_code


@pytest.mark.parametrize(
    ['cancel_reason', 'expected_reason'],
    [
        ('dispatch_reorder_required', 'dispatch_reorder'),
        ('dispatch_delivery_out_of_time', 'dispatch_cancel'),
        ('admin_reorder_required', 'admin_reorder'),
        (
            'admin_reorder_with_activity_penalty_required',
            'admin_reorder_with_activity_penalty',
        ),
        (
            'waybill_rebuild_reorder_required',
            'waybill_rebuild_reorder_required',
        ),
    ],
)
async def test_dispatch_cancel(
        taxi_cargo_orders,
        default_order_id,
        mock_intapi_orders_cancel,
        mock_dispatch_mark_fail,
        stq_runner,
        cancel_reason: str,
        expected_reason: str,
):
    """
        Happy path:
        1. dispatch -> lookup/cancel -> taxi-cancel
        2. processing2.0 -> taxi_order_cancelled
        3.  -> pass fail_reason to v1/waybill/mark/order-fail
    """
    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'cancel_reason': 'dispatch_reorder_required',
        },
    )
    assert response.status_code == 200

    mock_dispatch_mark_fail.expected_reason = expected_reason

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order-bad',
            'lookup_version': 1,
            'has_performer': True,
        },
    )
    assert mock_dispatch_mark_fail.handler.times_called == 0


async def test_dispatch_cancel_taxi_error(
        taxi_cargo_orders,
        default_order_id,
        mock_intapi_orders_cancel,
        mock_dispatch_mark_fail,
        stq_runner,
        cancel_reason='dispatch_reorder_required',
        expected_reason='dispatch_cancel',
):
    """
        1. dispatch -> lookup/cancel -> taxi-cancel network timeout
        2. processing2.0 -> taxi_order_cancelled
        3.  -> pass dispatch_reorder to v1/waybill/mark/order-fail
    """
    mock_intapi_orders_cancel.status_code = 500

    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'cancel_reason': 'dispatch_reorder_required',
        },
    )
    assert response.status_code == 500

    mock_dispatch_mark_fail.expected_reason = 'dispatch_reorder'

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order-bad',
            'lookup_version': 1,
            'has_performer': True,
        },
    )
    assert mock_dispatch_mark_fail.handler.times_called == 0


@pytest.mark.now('2021-11-01T13:35:01+0000')
@pytest.mark.config(
    CARGO_ORDERS_ORDER_CANCEL_CHECK_DRAFT_ALIVE={
        'enabled': True,
        'waiting_time_after_expired_sec': 60,
    },
)
async def test_order_cancel_draft_expired(
        taxi_cargo_orders,
        mock_intapi_orders_cancel,
        set_order_properties,
        default_order_id,
):
    set_order_properties(
        default_order_id,
        commit_state='draft',
        created='2021-11-01T13:30:01+0000',
    )
    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2021-11-01T13:35:01+0000')
@pytest.mark.parametrize(
    'commit_state, expected_code',
    [('draft', 'bad_state'), ('failed', 'gone')],
)
async def test_order_cancel_commit_race(
        taxi_cargo_orders,
        mock_intapi_orders_cancel,
        set_order_properties,
        default_order_id,
        commit_state: str,
        expected_code: str,
):
    set_order_properties(
        default_order_id,
        commit_state=commit_state,
        created='2021-11-01T13:30:01+0000',
    )
    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
        },
    )

    assert response.status_code == 409
    assert response.json()['code'] == expected_code


@pytest.mark.parametrize(
    'enabled, activity_remove_tanker_key, need_autoreorder_tanker_key',
    [
        (False, None, None),
        (False, None, 'need_autoreorder_tanker_key'),
        (False, 'activity_remove_tanker_key', None),
        (False, 'activity_remove_tanker_key', 'need_autoreorder_tanker_key'),
        (True, None, None),
        (True, None, 'need_autoreorder_tanker_key'),
        (True, 'activity_remove_tanker_key', None),
        (True, 'activity_remove_tanker_key', 'need_autoreorder_tanker_key'),
    ],
)
@pytest.mark.parametrize(
    'reason_ids_chain, cancel_reason',
    [
        (['folder_id', 'reason_id'], 'dispatch_reorder_required'),
        (None, 'dispatch_reorder_required'),
        (['folder_id', 'reason_id'], 'admin_reorder_required'),
        (None, 'admin_reorder_required'),
        (
            ['folder_id', 'reason_id'],
            'admin_reorder_with_activity_penalty_required',
        ),
        (None, 'admin_reorder_with_activity_penalty_required'),
        (None, 'waybill_rebuild_reorder_required'),
    ],
)
async def test_order_cancel_with_admin_reason(
        taxi_cargo_orders,
        mockserver,
        taxi_config,
        mock_intapi_orders_cancel,
        default_order_id,
        testpoint,
        enabled: bool,
        activity_remove_tanker_key: str,
        need_autoreorder_tanker_key: str,
        reason_ids_chain: list,
        cancel_reason: str,
):
    childs = [{'id': 'reason_id', 'menu_item_tanker_key': 'reason_tanker_key'}]
    if activity_remove_tanker_key:
        childs[-1]['activity_remove_tanker_key'] = activity_remove_tanker_key
    if need_autoreorder_tanker_key:
        childs[-1]['need_autoreorder_tanker_key'] = need_autoreorder_tanker_key
    taxi_config.set(
        CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2={
            'enabled': enabled,
            'cancel_button_tanker_key': 'order_cancel',
            'cancel_reason_tree': [
                {
                    'childs': childs,
                    'id': 'folder_id',
                    'menu_item_tanker_key': 'folder_tanker_key',
                },
            ],
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/cancelled',
    )
    async def _mock_callback(request):
        assert request.json == {
            'park_id': 'park_id1',
            'driver_profile_id': 'driver_id1',
            'setcar_id': '1234',
            'reason': 'cargo autoreorder by performer',
            'origin': 'cargo',
        }

        return mockserver.make_response(
            json={'status': 'cancelled'}, status=200,
        )

    @testpoint('order-cancel::is_activity_penalty_required')
    def _is_activity_penalty_required(data):
        assert data['is_activity_penalty_required'] == (
            enabled
            and activity_remove_tanker_key is not None
            and reason_ids_chain is not None
            or (reason_ids_chain is None or not enabled)
            and cancel_reason == 'admin_reorder_with_activity_penalty_required'
        )

    response = await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
            'reason_ids_chain': reason_ids_chain,
            'cancel_reason': cancel_reason,
        },
    )

    assert response.status_code == 200
    assert response.json() == {'cancel_state': 'free'}


@pytest.mark.parametrize('orders_should_notify', [False, True])
@pytest.mark.parametrize('claims_should_notify', [False, True])
async def test_order_api_should_notify(
        taxi_cargo_orders,
        mockserver,
        taxi_config,
        mock_intapi_orders_cancel,
        default_order_id,
        orders_should_notify: bool,
        claims_should_notify: bool,
):
    taxi_config.set(
        CARGO_DRIVER_ORDERS_APP_API_SHOULD_NOTIFY={
            'orders_should_notify': orders_should_notify,
            'claims_should_notify': claims_should_notify,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/cancelled',
    )
    async def _mock_callback(request):
        if orders_should_notify:
            assert request.json['should_notify']
        else:
            assert 'should_notify' not in request.json

    await taxi_cargo_orders.post(
        '/v1/order/cancel',
        json={
            'order_id': default_order_id,
            'cancel_state': 'free',
            'dispatch_version': 1,
            'reason_ids_chain': None,
            'cancel_reason': 'admin_reorder_with_activity_penalty_required',
        },
    )

    assert _mock_callback.times_called == 1


@pytest.mark.parametrize(
    'cancel_request_token', [None, 'cargo-dispatch/some_token'],
)
async def test_cancel_request_token(
        taxi_cargo_orders,
        mock_intapi_orders_cancel,
        fetch_order,
        default_order_id,
        cancel_request_token,
):
    request = {
        'order_id': default_order_id,
        'cancel_state': 'free',
        'dispatch_version': 1,
        'reason_ids_chain': ['cancel_order', 'cancel_order__invalid_status'],
        'cancel_reason': 'admin_reorder_required',
    }

    if cancel_request_token is not None:
        request['cancel_request_token'] = cancel_request_token

    response = await taxi_cargo_orders.post('/v1/order/cancel', json=request)

    assert response.status_code == 200

    order = fetch_order(default_order_id)
    assert order.cancel_request_token == cancel_request_token
