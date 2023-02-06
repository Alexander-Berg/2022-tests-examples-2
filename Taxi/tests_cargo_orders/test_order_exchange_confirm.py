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


DISPATCH_POINT_BASE: dict = {'type': 'source', 'label': 'label', 'phones': []}

DISPATCH_ROUTE_POINT: dict = {
    'address': {'fullname': 'SEND IT TO ORDERS', 'coordinates': [1.0, 2.0]},
    **DISPATCH_POINT_BASE,
}

DISPATCH_NEW_ROUTE: list = [{'id': 1, **DISPATCH_ROUTE_POINT}]

DISPATCH_NEW_POINT: dict = {
    **DISPATCH_POINT_BASE,
    'need_confirmation': True,
    'visit_order': 1,
    'actions': [],
}

DISPATCH_NEW_ROUTE_BATCH: list = [
    {
        'address': {'coordinates': [1, 2], 'fullname': 'Огородный проезд, 12'},
        'id': 1,
        'label': 'Получение 1',
        'phones': [],
        'type': 'source',
    },
    {
        'address': {'coordinates': [1, 2], 'fullname': 'Огородный проезд, 12'},
        'id': 2,
        'label': 'Получение 2',
        'phones': [],
        'type': 'source',
    },
    {
        'address': {'coordinates': [1, 2], 'fullname': 'Огородный проезд, 12'},
        'id': 3,
        'label': 'Вручение 1',
        'phones': [],
        'type': 'destination',
    },
    {
        'address': {'coordinates': [1, 2], 'fullname': 'Огородный проезд, 12'},
        'id': 4,
        'label': 'Вручение 2',
        'phones': [],
        'type': 'destination',
    },
]

DISPATCH_NEW_POINT_BATCH: dict = {
    'address': {'coordinates': [1, 2], 'fullname': 'Огородный проезд, 12'},
    'id': 3,
    'label': 'Вручение 1',
    'phones': [],
    'type': 'destination',
}


@pytest.fixture(name='orders_confirm_point')
def _orders_confirm_point(taxi_cargo_orders):
    async def _wrapper(order_id: str, headers=None, expected_request=None):
        if headers is None:
            headers = DEFAULT_HEADERS
        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/exchange/confirm',
            json={
                'cargo_ref_id': 'order/' + order_id,
                'last_known_status': 'pickup_confirmation',
                'point_id': 1,
                'idempotency_token': 'some_token',
            },
            headers=headers,
        )
        return response

    return _wrapper


async def test_happy_path(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['new_status'] == 'delivering'
    assert resp_body['result'] == 'confirmed'
    assert resp_body['state_version'] == 'v0_1'
    # TODO: check full response body


# TODO: remove in <Задача на исправление тестов>
async def set_segments_status(waybill_info: dict, segment_status: str):
    for segment in waybill_info['execution']['segments']:
        segment['status'] = segment_status


# TODO: remove in <Задача на исправление тестов>
def set_each_point_resolved(waybill_info):
    for point in waybill_info['execution']['points']:
        point['is_resolved'] = True
        point['resolution'] = {'is_visited': True, 'is_skipped': False}


# TODO: remove in <Задача на исправление тестов>
def set_first_point_skipped(waybill_info):
    first_point = waybill_info['execution']['points'][0]
    first_point['is_resolved'] = True
    first_point['resolution'] = {'is_visited': False, 'is_skipped': True}
    first_point['is_return_required'] = True


async def test_rejected(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
        my_waybill_info,
):
    await set_segments_status(my_waybill_info, 'ready_for_pickup_confirmation')

    mock_dispatch_exchange_confirm.response = {
        'result': 'rejected',
        'new_status': 'pickup_confirmation',
        'new_route': DISPATCH_NEW_ROUTE,
        'waybill_info': my_waybill_info,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['new_status'] == 'pickup_confirmation'
    assert resp_body['result'] == 'rejected'


async def test_conflict(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
        mockserver,
):
    mock_dispatch_exchange_confirm.response = mockserver.make_response(
        status=409,
        json={'code': 'state_mismatch', 'message': 'confirmation conflict'},
    )

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 409


@pytest.mark.parametrize(
    'last_status,result_code', [('complete', 200), ('new', 409)],
)
async def test_confirm_without_point(
        taxi_cargo_orders,
        default_order_id,
        last_status: str,
        result_code: int,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/confirm',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': last_status,
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == result_code


async def test_new_point(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    """
    TODO: confirm first point and assert that next_point_id == second_point_id
    """
    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['new_point']['id'] == 642499


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(
        orders_confirm_point, default_order_id, bad_header: str,
):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await orders_confirm_point(
        default_order_id, headers=headers_bad_driver,
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'not_authorized'
    assert response.json()['message'] == 'Попробуйте снова'


async def test_last_waybill_point(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
        my_waybill_info,
):
    set_each_point_resolved(my_waybill_info)

    mock_dispatch_exchange_confirm.response = {
        'result': 'confirmed',
        'new_status': 'delivered',
        'new_route': DISPATCH_NEW_ROUTE,
        'waybill_info': my_waybill_info,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['result'] == 'confirmed'
    assert 'new_point' not in resp_body


async def test_no_return_point_in_response_route(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['result'] == 'confirmed'
    point_types = [point['type'] for point in resp_body['new_route']]
    assert 'return' not in point_types


async def test_return_point_in_response_route(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
        my_waybill_info,
):
    set_first_point_skipped(my_waybill_info)
    mock_dispatch_exchange_confirm.response = {
        'result': 'confirmed',
        'new_status': 'delivered',
        'new_route': DISPATCH_NEW_ROUTE,
        'waybill_info': my_waybill_info,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    point_types = [point['type'] for point in resp_body['new_route']]
    assert 'return' in point_types


async def test_confirm_request(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    mock_dispatch_exchange_confirm.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'point_id': 1,
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'async_timer_calculation_supported': False,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_async_timer_calculation': '9.00'},
        },
    },
)
async def test_confirm_request_async_timer(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    mock_dispatch_exchange_confirm.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'point_id': 1,
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'async_timer_calculation_supported': True,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 1,
                                'arg_name': (
                                    'prev_source_points_duplicates_count'
                                ),
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'skip_arrive_screen': True,
                'dialog_between_source_points': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
            },
        },
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 2,
                                'arg_name': 'active_segments_count',
                                'arg_type': 'int',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'skip_arrive_screen': False,
                'dialog_after_last_source_point': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
                'dialog_after_new_points_added': {
                    'title_tanker_key': (
                        'actions.show_dialog.default_batch_title'
                    ),
                    'message_tanker_key': (
                        'actions.show_dialog.default_batch_message'
                    ),
                    'button_tanker_key': (
                        'actions.show_dialog.default_batch_button'
                    ),
                },
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
async def test_show_dialog(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        default_order_id,
        my_batch_waybill_info,
):

    my_batch_waybill_info['execution']['points'][1]['is_resolved'] = True

    mock_dispatch_exchange_confirm.response = {
        'result': 'confirmed',
        'new_status': 'pickup_confirmation',
        'new_route': DISPATCH_NEW_ROUTE_BATCH,
        'new_point': DISPATCH_NEW_POINT_BATCH,
        'waybill_info': my_batch_waybill_info,
    }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/confirm',
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 2,
            'idempotency_token': 'some_token',
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['new_status'] == 'delivering'
    assert resp_json['new_point'] == {
        'actions': [
            {
                'button': 'Ок',
                'message': 'Не забудьте забрать второй заказ',
                'tag': 'last_source_point_notify',
                'title': 'Еще заказ',
                'type': 'show_dialog',
            },
            {'type': 'arrived_at_point'},
            {'type': 'show_act'},
        ],
        'id': 4,
        'label': 'Точка Б21',
        'need_confirmation': True,
        'phones': [
            {
                'background_loading': False,
                'label': 'Получатель2',
                'type': 'destination',
                'view': 'main',
            },
        ],
        'type': 'destination',
        'visit_order': 3,
        'segment_id': 'seg_2',
        'comment': '',
        'comment_type': 'plain',
        'number_of_parcels': 1,
    }


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'exchange_confirm_enabled': True,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
        'cannot_check_payment_tanker_key': (
            'errors.cannot_check_phoenix_payment'
        ),
        'ignore_check_payment_admin_exchange_init': True,
    },
    CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
)
@pytest.mark.parametrize(
    'is_paid, '
    'claims_response_status, '
    'expected_status_code, '
    'code, '
    'message',
    [
        (True, 'success', 200, None, None),
        (False, 'success', 404, 'payment_not_found', 'Заказ не оплачен'),
        (
            True,
            'not_found',
            404,
            'order_not_found',
            'Нет возможности проверить оплату',
        ),
        (True, 'failed', 500, '500', 'Internal Server Error'),
    ],
)
async def test_phoenix_flow(
        orders_confirm_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_exchange_confirm,
        mock_claims_phoenix_traits,
        default_order_id,
        mockserver,
        is_paid,
        claims_response_status,
        expected_status_code,
        code,
        message,
):
    mock_claims_phoenix_traits.claims_response_status = claims_response_status

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/v1/claims/payment-status',
    )
    def _mock_claim_state(request):
        assert request.args['claim_id'] == 'claim_uuid_1'
        return mockserver.make_response(json={'is_paid': is_paid}, status=200)

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == expected_status_code
    if response.status_code != 200:
        assert response.json() == {'code': code, 'message': message}


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'exchange_confirm_enabled': True,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
        'cannot_check_payment_tanker_key': (
            'errors.cannot_check_phoenix_payment'
        ),
        'ignore_check_payment_admin_exchange_init': True,
    },
    CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
)
async def test_phoenix_flow_cache_hit(
        orders_confirm_point,
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        mock_admin_claims_phoenix_traits,
        mock_dispatch_exchange_confirm,
        mock_claims_phoenix_traits,
        default_order_id,
        mockserver,
):
    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/v1/claims/payment-status',
    )
    def _mock_claim_state(request):
        assert request.args['claim_id'] == 'claim_uuid_1'
        return mockserver.make_response(json={'is_paid': True}, status=200)

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200
    assert mock_claims_phoenix_traits.handler.times_called == 0


async def test_exchange_confirm_wrong_params(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/confirm',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': '',
            'last_known_status': '',
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Parse error at pos 44, path \'last_known_status\': Value \'\' is not '
            'parseable into handlers::ClaimTaximeterStatus, the latest token '
            'was : ""'
        ),
    }
