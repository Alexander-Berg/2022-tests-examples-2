import pytest


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


EXP_ROBOCALL_TYPE = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_orders_client_robocall',
    consumers=['cargo-orders/client-robocall'],
    clauses=[],
    default_value={'enabled': True, 'robocall_type': 'eats_core'},
)


def find_action(json, action_type):
    for action in json['current_point']['actions']:
        if action['type'] == action_type:
            return action
    return None


async def call_and_check_robocall(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        fetch_order_client_robocall,
):
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert find_action(response.json(), 'robocall') is not None

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    assert stq.cargo_orders_client_robocall.times_called == 1
    stq_call = stq.cargo_orders_client_robocall.next_call()
    assert stq_call['id'] == f'{default_order_id}_{point_id}'

    kwargs = stq_call['kwargs']
    assert kwargs['cargo_order_id'] == default_order_id
    assert kwargs['point_id'] == point_id

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'calling'


@pytest.mark.now('2021-10-10T10:00:00+03:00')
@EXP_ROBOCALL_TYPE
async def test_robocall_happy_path(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        fetch_order_client_robocall,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',
    }

    await call_and_check_robocall(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        fetch_order_client_robocall,
    )

    # Duplicated call must not create a new record.
    await call_and_check_robocall(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        fetch_order_client_robocall,
    )


@pytest.mark.now('2021-10-10T10:00:00+03:00')
async def test_disabled_robocall_type(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        fetch_order_client_robocall,
        mock_driver_tags_v1_match_profile,
):
    # exp_cargo_orders_robocall_actions() is enabled
    # but @EXP_ROBOCALL_TYPE is disabled.
    # Robocall action is allowed but robocall is not configured.

    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',
    }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    # Robocall action button must be removed when robocall is finished.
    assert find_action(response.json(), 'robocall') is None

    dialog_action = find_action(response.json(), 'show_dialog')
    assert dialog_action == {
        'type': 'show_dialog',
        'tag': 'robocall_client_not_answered',
        'title': 'Не дозвонились',
        'message': 'Позвоните в поддержку',
        'button': 'Хорошо4',
    }

    assert stq.cargo_orders_client_robocall.times_called == 0

    order_client_robocall = fetch_order_client_robocall(
        default_order_id,
        my_waybill_info['execution']['points'][0]['point_id'],
    )
    assert order_client_robocall.status == 'finished'
    assert order_client_robocall.resolution == 'disabled_by_experiment'


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_robocall_no_auth(
        taxi_cargo_orders, stq, my_waybill_info, default_order_id, bad_header,
):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=headers_bad_driver,
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }

    assert stq.cargo_orders_client_robocall.times_called == 0


@pytest.mark.parametrize(
    'order_id, expected_status, expected_body',
    [
        (
            '00000000-1111-2222-3333-444444444444',
            404,
            {'code': 'Not found', 'message': 'Waybill is empty'},
        ),
        (
            '123',
            400,
            {'code': 'bad_request', 'message': 'Invalid cargo_ref_id'},
        ),
    ],
)
async def test_robocall_order_not_found(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        fetch_order_client_robocall,
        order_id,
        expected_status,
        expected_body,
):
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_body

    assert stq.cargo_orders_client_robocall.times_called == 0


async def test_robocall_point_not_found(
        taxi_cargo_orders, stq, default_order_id, fetch_order_client_robocall,
):
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 123,
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'Not found',
        'message': 'claim_point_id is not found',
    }

    assert stq.cargo_orders_client_robocall.times_called == 0


async def test_robocall_unexpected_status(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'pickuped'

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'Conflict',
        'message': 'Robocall action is not allowed at the moment',
    }

    assert stq.cargo_orders_client_robocall.times_called == 0


@pytest.mark.now('2021-10-10T10:00:00+03:00')
@pytest.mark.parametrize(
    'promise_min_at, expected_status',
    [('2021-10-10T10:00:01+03:00', 409), ('2021-10-10T10:00:00+03:00', 200)],
)
async def test_robocall_unexpected_time(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        promise_min_at,
        expected_status,
        mock_driver_tags_v1_match_profile,
):
    await exp_cargo_orders_robocall_actions()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': promise_min_at,
    }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == expected_status


@pytest.mark.now('2021-10-10T10:00:00+03:00')
@EXP_ROBOCALL_TYPE
async def test_notification_happy_path(
        taxi_cargo_orders,
        mockserver,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        exp_cargo_client_notification,
        mock_driver_tags_v1_match_profile,
        eats_order_nr='000000-000001',
):
    await exp_cargo_orders_robocall_actions()
    await exp_cargo_client_notification()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',
    }
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = eats_order_nr

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_notification(request):
        assert (
            request.headers['X-Idempotency-Key']
            == f'{default_order_id}_{point_id}'
        )
        assert request.json['order_nr'] == eats_order_nr
        assert request.json['notification_event'] == 'notification_code'
        assert request.json['allowed_channels'] == ['push', 'sms']
        return mockserver.make_response(
            status=200, json={'notification_id': '123'},
        )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert mock_notification.times_called == 1


@pytest.mark.now('2021-10-10T10:00:00+03:00')
@EXP_ROBOCALL_TYPE
async def test_notification_failed(
        taxi_cargo_orders,
        mockserver,
        my_waybill_info,
        default_order_id,
        exp_cargo_orders_robocall_actions,
        exp_cargo_client_notification,
        mock_driver_tags_v1_match_profile,
        eats_order_nr='000000-000001',
):
    await exp_cargo_orders_robocall_actions()
    await exp_cargo_client_notification()

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',
    }
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = eats_order_nr

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_notification(request):
        assert (
            request.headers['X-Idempotency-Key']
            == f'{default_order_id}_{point_id}'
        )
        assert request.json['order_nr'] == eats_order_nr
        assert request.json['notification_event'] == 'notification_code'
        assert request.json['allowed_channels'] == ['push', 'sms']
        return mockserver.make_response(
            status=400, json={'code': 'error', 'message': 'text'},
        )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )
    # Проблема с отправкой нотификации не должна ломать дальнейшую работу
    # робокола.
    assert response.status_code == 200

    assert mock_notification.times_called == 1
