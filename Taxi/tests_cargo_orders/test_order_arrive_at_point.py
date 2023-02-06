import copy
import operator

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


@pytest.mark.parametrize(
    'claims_response_code,point_id,result_code',
    [
        (200, 100500, 200),
        (404, 100500, 404),
        (409, 100500, 409),
        (500, 100500, 500),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_orders_yagr_store_driver_position',
    consumers=['cargo-orders/yagr-store-driver-position'],
    default_value={'enabled': True},
)
async def test_claims_exchange_statuses(
        taxi_cargo_orders,
        mockserver,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        claims_response_code: int,
        point_id: int,
        result_code: int,
        my_waybill_info,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return mockserver.make_response(
            json={'new_status': 'new', 'waybill_info': my_waybill_info}
            if claims_response_code == 200
            else {'code': 'not_found', 'message': 'some message'},
            status=claims_response_code,
        )

    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _mock_position_store(request):
        return mockserver.make_response(
            status=result_code,
            headers={'X-Polling-Power-Policy': 'policy'},
            content_type='application/json',
        )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': point_id,
            'location_data': {'a': []},
        },
    )
    assert response.status_code == result_code


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(taxi_cargo_orders, default_order_id, bad_header: str):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=headers_bad_driver,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 123123,
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


def param_expect_door_code_comment(enabled_by_exp):
    return pytest.param(
        enabled_by_exp,
        marks=pytest.mark.experiments3(
            is_config=True,
            name='cargo_orders_add_door_code_comment',
            consumers=['cargo-orders/build-point-comment'],
            default_value={'enabled': enabled_by_exp},
        ),
    )


@pytest.mark.parametrize(
    'expect_door_code_comment',
    [
        param_expect_door_code_comment(True),
        param_expect_door_code_comment(False),
    ],
)
async def test_batch(
        taxi_cargo_orders,
        mockserver,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_batch_waybill_info,
        expect_door_code_comment,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return {'new_status': 'new', 'waybill_info': my_batch_waybill_info}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 1,
        },
    )

    assert response.status_code == 200
    expect_response = {
        'new_point': {
            'actions': [{'type': 'arrived_at_point'}, {'type': 'show_act'}],
            'id': 3,
            'label': 'Точка А2',
            'need_confirmation': True,
            'leave_under_door': True,
            'meet_outside': False,
            'no_door_call': True,
            'modifier_age_check': True,
            'client_name': 'Иван',
            'phones': [
                {
                    'background_loading': False,
                    'label': 'Отправитель2',
                    'type': 'source',
                    'view': 'main',
                },
            ],
            'type': 'source',
            'visit_order': 2,
            'segment_id': 'seg_2',
            'comment': (
                'Код от подъезда/домофона: A2_door_code.\n'
                'Комментарий: A2_comment'
            ),
            'comment_type': 'plain',
            'number_of_parcels': 1,
        },
        'new_route': [
            {
                'address': {
                    'coordinates': [1.0, 2.0],
                    'fullname': 'Точка А1',
                    'shortname': 'Точка А1',
                    'sflat': '123',
                },
                'id': 1,
                'items': [],
                'label': 'Получение 1',
                'phones': [
                    {
                        'background_loading': False,
                        'label': 'Отправитель1',
                        'type': 'source',
                        'view': 'main',
                    },
                ],
                'type': 'source',
                'number_of_parcels': 1,
            },
            {
                'address': {
                    'coordinates': [3.0, 4.0],
                    'fullname': 'Точка А2',
                    'comment': 'A2_comment',
                    'comment_type': 'plain',
                    'door_code': 'A2_door_code',
                    'shortname': 'Точка А2',
                },
                'id': 3,
                'contact_name': 'Иван',
                'items': [],
                'label': 'Получение 2',
                'phones': [
                    {
                        'background_loading': False,
                        'label': 'Отправитель2',
                        'type': 'source',
                        'view': 'main',
                    },
                ],
                'type': 'source',
                'number_of_parcels': 1,
            },
            {
                'address': {
                    'coordinates': [5.0, 6.0],
                    'fullname': 'Точка Б21',
                    'shortname': 'Точка Б21',
                },
                'id': 4,
                'items': [],
                'label': 'Выдача 1',
                'phones': [
                    {
                        'background_loading': False,
                        'label': 'Получатель2',
                        'type': 'destination',
                        'view': 'main',
                    },
                ],
                'type': 'destination',
                'number_of_parcels': 1,
            },
            {
                'address': {
                    'coordinates': [7.0, 8.0],
                    'fullname': 'Точка Б11',
                    'shortname': 'Точка Б11',
                },
                'id': 2,
                'items': [],
                'label': 'Выдача 2',
                'phones': [
                    {
                        'background_loading': False,
                        'label': 'Получатель1',
                        'type': 'destination',
                        'view': 'main',
                    },
                ],
                'type': 'destination',
                'number_of_parcels': 1,
            },
        ],
        'new_status': 'new',
        'state_version': 'v0_2',
        'order_comment': (
            'Заказ с подтверждением по СМС.\n'
            'Комментарий: seg_2_claim_comment\n'
            'Количество точек маршрута: 3.'
        ),
        'order_comment_type': 'plain',
    }

    if expect_door_code_comment is False:
        expect_response['new_point']['comment'] = 'Комментарий: A2_comment'

    assert response.json() == expect_response


@pytest.mark.translations(
    cargo={
        'custom.point_label.pull_dispatch_return': {
            'en': 'pull_dispatch_return_label',
        },
    },
)
async def test_pull_dispatch_return_label(
        taxi_cargo_orders,
        mockserver,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_multipoints_waybill_info,
):
    my_multipoints_waybill_info['dispatch']['is_pull_dispatch'] = True
    my_multipoints_waybill_info['execution']['points'][2][
        'location'
    ] = my_multipoints_waybill_info['execution']['points'][0]['location']

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return {
            'new_status': 'new',
            'waybill_info': my_multipoints_waybill_info,
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 1,
        },
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert len(resp_body['new_route']) == 3

    labels = list(map(lambda x: x['label'], resp_body['new_route']))
    assert labels == ['Получение', 'Выдача 1', 'pull_dispatch_return_label']


@pytest.mark.translations(
    cargo={'custom.pickup.title': {'en': 'Custom pickup title'}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_localize_actions',
    consumers=['cargo-orders/build-actions'],
    clauses=[],
    default_value={'pickup_action_tanker_key': 'custom.pickup.title'},
)
async def test_custom_translations(
        taxi_cargo_orders,
        mockserver,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_waybill_info,
):
    waybill_info = copy.deepcopy(my_waybill_info)
    waybill_info['execution']['segments'][0]['status'] = 'pickup_arrived'

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_arrive(request):
        return mockserver.make_response(
            json={'new_status': 'new', 'waybill_info': waybill_info},
        )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 100500,
        },
    )
    assert response.status_code == 200
    pickup_actions = [
        x
        for x in response.json()['new_point']['actions']
        if x['type'] == 'pickup'
    ]
    assert len(pickup_actions) == 1
    assert pickup_actions[0]['title'] == 'Custom pickup title'


@pytest.mark.parametrize('with_dropoff_title', [True, False])
async def test_post_payment_flow_action(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
        mock_dispatch_arrive_at_point,
        mock_driver_tags_v1_match_profile,
        with_dropoff_title: bool,
        point_id=100500,
):
    await exp_cargo_orders_post_payment_flow(
        with_dropoff_title=with_dropoff_title,
    )

    waybill_state.set_segment_status('delivery_arrived')
    waybill_state.set_post_payment()

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': point_id,
        },
    )
    assert response.status_code == 200

    actions = sorted(
        response.json()['new_point']['actions'],
        key=operator.itemgetter('type'),
    )
    dropoff_action = {
        'need_confirmation': True,
        'type': 'dropoff',
        'conditions': [],
    }
    if with_dropoff_title:
        # this title is shown on slider
        # https://st.yandex-team.ru/CARGODEV-4751
        dropoff_action['title'] = 'Получил оплату'
    expected_actions = [
        dropoff_action,
        {
            'type': 'external_flow',
            'service': 'cargo-payments',
            'title': 'Получил оплату',
            'payload': {'payment_ref_id': '123'},
        },
        {'type': 'show_act'},
    ]
    assert actions == expected_actions


@pytest.mark.parametrize(
    'enabled_by_config',
    (
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                        '__default__': {
                            'feature_support': {'order_picker_pickup': '9.40'},
                        },
                    },
                ),
            ],
        ),
    ),
)
@pytest.mark.parametrize(
    ('features', 'expected_action'),
    (([{'id': 'picker_order'}], True), ([], False)),
)
@pytest.mark.parametrize('was_ready_at', (True, False))
async def test_picker_order_action(
        taxi_cargo_orders,
        default_order_id,
        waybill_state,
        mock_dispatch_arrive_at_point,
        mock_driver_tags_v1_match_profile,
        my_waybill_info,
        features,
        expected_action,
        enabled_by_config,
        was_ready_at,
):
    waybill_state.set_segment_status('pickup_arrived')
    my_waybill_info['execution']['segments'][0]['claim_features'] = features
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = 'eda_order_id_1'
    if was_ready_at:
        my_waybill_info['execution']['points'][0][
            'was_ready_at'
        ] = '2020-08-18T13:56:49.939497+00:00'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 642499,
        },
    )
    assert response.status_code == 200
    actions = response.json()['new_point']['actions']
    picker_action = [a for a in actions if a['type'] == 'order_picker_pickup']
    pickup_action = [a for a in actions if a['type'] == 'pickup']
    if expected_action and enabled_by_config and not was_ready_at:
        assert picker_action == [
            {
                'type': 'order_picker_pickup',
                'external_order_id': 'eda_order_id_1',
            },
        ]
        assert not pickup_action
    else:
        assert not picker_action


@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_ui_build(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        pull_dispatch_enabled,
        mockserver,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return mockserver.make_response(
            json={
                'new_status': 'new',
                'waybill_info': waybill_info_pull_dispatch,
            },
            status=200,
        )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_driver_state_ui',
        consumers=['cargo-orders/ui'],
        clauses=[
            {
                'alias': 'lavka1',
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'arg_name': 'corp_client_id',
                        'set': [corp_client_id],
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'title': 'Лавка 1',
                'value': {
                    'screens': [
                        {
                            'name': 'arrive_screen',
                            'ui': {
                                'blocks': [
                                    {'type': 'cost_plate'},
                                    {'type': 'route'},
                                    {'type': 'comment'},
                                ],
                            },
                        },
                    ],
                },
            },
        ],
        default_value={},
    )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 751419,
        },
    )

    assert response.status_code == 200

    if not pull_dispatch_enabled:
        assert 'ui' not in response.json()
    else:
        assert 'ui' in response.json()
        assert response.json()['ui'] == {
            'blocks': [
                {'type': 'cost_plate'},
                {'type': 'route'},
                {'type': 'comment'},
            ],
        }
