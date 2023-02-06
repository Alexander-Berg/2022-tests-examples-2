import bson
import pytest

PARK_ID = 'park_id_0'
DRIVER_ID = 'driver'
UNIQUE_DRIVER_ID = 'unique_driver_0'
SESSION = 'test_session'
URL_V2 = 'v2/driver/money/order'

RESPONSE404 = {'code': '404', 'message': 'Not found'}


@pytest.mark.parametrize(
    (
        'order_id,handler,code,expected,billing,'
        'has_unique,has_activity,has_track,has_priority'
    ),
    [
        pytest.param(
            'yandex_no_price',
            URL_V2,
            200,
            'expected_v2_yandex.json',
            'billing_yandex.json',
            True,
            True,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_use_billing_order_cost.json',
                ),
            ),
        ),
        pytest.param(
            'yandex_no_price',
            URL_V2,
            200,
            'expected_v2_yandex_with_priority.json',
            'billing_yandex.json',
            True,
            False,
            True,
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_use_billing_order_cost.json',
                ),
            ),
        ),
        pytest.param(
            'park_no_price',
            URL_V2,
            200,
            'expected_v2_park.json',
            'billing_park.json',
            False,
            False,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_use_billing_order_cost.json',
                ),
            ),
        ),
        pytest.param(
            'yandex',
            URL_V2,
            200,
            'expected_v2_driver_fix.json',
            'billing_driver_fix.json',
            True,
            True,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_use_billing_order_cost.json',
                ),
            ),
        ),
        pytest.param(
            'yandex',
            URL_V2,
            200,
            'expected_v2_yandex.json',
            'billing_yandex.json',
            True,
            True,
            True,
            False,
        ),
        (
            'yandex',
            URL_V2,
            200,
            'expected_v2_subventions_without_comissions.json',
            'billing_subventions_without_comissions.json',
            True,
            False,
            False,
            False,
        ),
        (
            'yandex',
            URL_V2,
            200,
            'expected_v2_driver_fix.json',
            'billing_driver_fix.json',
            True,
            True,
            True,
            False,
        ),
        (
            'yandex',
            URL_V2,
            200,
            'expected_v2_driver_fix_tips.json',
            'billing_driver_fix_tips.json',
            True,
            False,
            True,
            False,
        ),
        (
            'park',
            URL_V2,
            200,
            'expected_v2_park.json',
            'billing_park.json',
            False,
            False,
            True,
            False,
        ),
        (
            'yandex_cancelled',
            URL_V2,
            200,
            'expected_v2_yandex_cancelled.json',
            [],
            True,
            True,
            False,
            False,
        ),
        (
            'yandex',
            URL_V2,
            200,
            'expected_v2_fixed_commission.json',
            'billing_yandex_positive_park_commission.json',
            True,
            True,
            True,
            False,
        ),
        (
            'not_found',
            URL_V2,
            404,
            '{"code":"404","message":"Not Found"}',
            [],
            False,
            False,
            False,
            False,
        ),
        (
            'yandex_wrong_driver',
            URL_V2,
            404,
            '{"code":"404","message":"Not Found"}',
            [],
            False,
            False,
            False,
            False,
        ),
        (
            'yandex_not_found_driver_id',
            URL_V2,
            404,
            '{"code":"404","message":"Not Found"}',
            [],
            False,
            False,
            False,
            False,
        ),
        pytest.param(
            'yandex',
            URL_V2,
            200,
            'expected_v2_yandex_hidden_fields.json',
            'billing_yandex.json',
            True,
            True,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_pro_hide_order_info.json',
                ),
            ),
        ),
        pytest.param(
            'park_freightage_contract',
            URL_V2,
            200,
            'expected_v2_show_freightage_button.json',
            'billing_park.json',
            False,
            False,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_pro_show_freightage_button.json',
                ),
            ),
            id='show_freightage_contract_button',
        ),
        pytest.param(
            'park_freightage_contract_overdue',
            URL_V2,
            200,
            'expected_v2_freightage_overdue.json',
            'billing_park.json',
            False,
            False,
            True,
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_pro_show_freightage_button.json',
                ),
            ),
            id='hide_freightage_contract_button_due_to_overdued',
        ),
        pytest.param(
            'freightage_contract_cancelled',
            URL_V2,
            200,
            'expected_v2_yandex_cancelled.json',
            'billing_park.json',
            True,
            True,
            False,
            False,
            id='hide_freightage_contract_button_due_to_status',
        ),
        pytest.param(
            'park_freightage_contract',
            URL_V2,
            200,
            'expected_v2_hide_freightage_button.json',
            'billing_park.json',
            False,
            False,
            True,
            False,
            id='hide_freightage_contract_button_due_to_experiment',
        ),
    ],
)
@pytest.mark.now('2019-12-1T00:00:00Z')
async def test_driver_money_order(
        taxi_driver_money,
        mocked_time,
        load_json,
        driver_orders,
        billing_reports,
        unique_drivers,
        driver_metrics_storage,
        geotracks,
        order_id,
        handler,
        code,
        expected,
        billing,
        has_activity,
        has_priority,
        has_track,
        has_unique,
):
    assert not (
        has_activity and has_priority
    ), 'has_activity and has_priority should be set separately'

    billing_reports.add_journal_entries(
        order_id, load_json(billing) if isinstance(billing, str) else billing,
    )
    if has_unique:
        unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    if has_activity:
        driver_metrics_storage.set_metric_event(
            driver_metrics_storage.USE_ACTIVITY, order_id, 2, 'long',
        )
    if has_priority:
        driver_metrics_storage.set_metric_event(
            driver_metrics_storage.USE_PRIORITY,
            order_id,
            {
                'priority_change': 2,
                'priority_absolute': 5,
                'completion_scores_change': -3,
            },
            'long',
        )
    if has_track:
        geotracks.set_response(load_json('geotracks.json'))

    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': order_id},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )

    assert response.status_code == code
    assert driver_orders.times_called == 1
    if code == 200:
        assert billing_reports.journal_calls == 1
        assert unique_drivers.calls == 1
        assert (
            has_unique
            and driver_metrics_storage.calls == 1
            or not has_unique
            and driver_metrics_storage.calls == 0
        )
        if has_track:
            assert geotracks.calls == 1

        expected_json = load_json(expected)
        expected_json['id'] = order_id
        assert response.json() == expected_json
    else:
        assert response.text == expected


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_money_order_show_callcenter_price',
    consumers=['driver-money/context'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    is_config=False,
)
@pytest.mark.now('2019-12-1T00:00:00Z')
async def test_driver_money_order_callcenter_price(
        taxi_driver_money,
        mockserver,
        load_json,
        driver_orders,
        billing_reports,
        unique_drivers,
        driver_metrics_storage,
        geotracks,
):
    order_id = 'yandex'
    billing_reports.add_journal_entries(
        order_id, load_json('billing_yandex.json'),
    )
    unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    driver_metrics_storage.set_metric_event(
        driver_metrics_storage.USE_ACTIVITY, order_id, 2, 'long',
    )
    geotracks.set_response(load_json('geotracks.json'))

    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def _order_fields(request):
        response = {
            'doc': {
                'order': {
                    'current_prices': {
                        'final_cost_meta': {
                            'driver': {'callcenter_delta': 15.0000},
                        },
                    },
                },
            },
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response),
        )

    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': order_id},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )

    assert response.status_code == 200
    assert driver_orders.times_called == 1
    assert _order_fields.times_called == 1
    expected_json = load_json('expected_v2_yandex_callcenter.json')
    expected_json['id'] = order_id
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'order_id,code,expected',
    [
        ('yandex', 200, 'expected_v2_yandex.json'),
        ('not_found', 404, '{"code":"404","message":"Not Found"}'),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_money_use_fleet_orders_details',
    consumers=['driver_money/v2_driver_money_order'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    is_config=False,
)
@pytest.mark.now('2019-12-1T00:00:00Z')
async def test_driver_money_order_fleet_orders(
        taxi_driver_money,
        mockserver,
        load_json,
        driver_orders,
        unique_drivers,
        driver_metrics_storage,
        geotracks,
        order_id,
        code,
        expected,
):
    @mockserver.json_handler(
        '/fleet-orders/internal/fleet-orders/orders/v1/order/calculation',
    )
    def mock_fleet_orders(request):
        if code != 200:
            return mockserver.make_response(json=RESPONSE404, status=404)
        return load_json('fleet_orders.json')

    unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    driver_metrics_storage.set_metric_event(
        driver_metrics_storage.USE_ACTIVITY, order_id, 2, 'long',
    )
    geotracks.set_response(load_json('geotracks.json'))

    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': order_id},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )

    assert response.status_code == code
    assert driver_orders.times_called == 1
    if code == 200:
        assert mock_fleet_orders.times_called == 1
        assert unique_drivers.calls == 1
        assert driver_metrics_storage.calls == 1
        assert geotracks.calls == 1

        expected_json = load_json(expected)
        expected_json['id'] = order_id
        assert response.json() == expected_json
    else:
        assert response.text == expected


@pytest.mark.parametrize(
    'claim_response, expected_response, claim_handler_calls',
    [
        # Disabled experiments case
        pytest.param(
            '404_response.json',
            'expected_v2_driver_fix.json',
            0,
            marks=(pytest.mark.now('2019-12-1T00:00:00Z')),
        ),
        # Simple claim phone calls case
        pytest.param(
            'claim_response.json',
            'expected_v2_with_cargo_phones.json',
            1,
            marks=(
                pytest.mark.now('2019-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history_for_claims.json',
                ),
            ),
        ),
        # Simple claim without phones (expired)
        pytest.param(
            'claim_response.json',
            'expected_v2_with_cargo.json',
            1,
            marks=(
                pytest.mark.now('2020-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history_for_claims.json',
                ),
            ),
        ),
        # cargo-claims 404 response
        pytest.param(
            '404_response.json',
            'expected_v2_driver_fix.json',
            1,
            marks=(
                pytest.mark.now('2019-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history_for_claims.json',
                ),
            ),
        ),
        # Simple order phone calls case
        pytest.param(
            '404_response.json',
            'expected_v2_with_order_phones.json',
            0,
            marks=(
                pytest.mark.now('2019-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history.json',
                ),
            ),
        ),
        # Simple order, but phones expired
        pytest.param(
            '404_response.json',
            'expected_v2_driver_fix.json',
            0,
            marks=(
                pytest.mark.now('2020-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history.json',
                ),
            ),
        ),
        # Both enabled, claim in priority
        pytest.param(
            'claim_response.json',
            'expected_v2_with_cargo_phones.json',
            1,
            marks=(
                pytest.mark.now('2019-12-1T00:00:00Z'),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history_for_claims.json',
                ),
                pytest.mark.experiments3(
                    filename='experiments3_call_from_history.json',
                ),
            ),
        ),
    ],
)
async def test_driver_money_order_with_phones(
        load_json,
        unique_drivers,
        driver_metrics_storage,
        geotracks,
        taxi_driver_money,
        driver_orders,
        mockserver,
        billing_reports,
        claim_response,
        expected_response,
        claim_handler_calls,
):
    order_id = 'yandex'
    billing_reports.add_journal_entries(
        order_id, load_json('billing_driver_fix.json'),
    )
    unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    driver_metrics_storage.set_metric_event(
        driver_metrics_storage.USE_ACTIVITY, order_id, 2, 'long',
    )
    geotracks.set_response(load_json('geotracks.json'))

    @mockserver.json_handler('/cargo-claims/v1/claims/taximeter-history')
    def mock_claims(request):
        return load_json(claim_response)

    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': order_id},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
    assert mock_claims.times_called == claim_handler_calls


@pytest.mark.parametrize(
    'order_id,expected,billing',
    [
        (
            'yandex',
            'expected_v2_subventions_without_comissions_late_holded.json',
            'billing_subventions_without_comissions.json',
        ),
    ],
)
@pytest.mark.now('2019-12-5T00:00:00Z')
async def test_driver_money_order_late_holded(
        taxi_driver_money,
        load_json,
        mocked_time,
        driver_orders,
        driver_metrics_storage,
        geotracks,
        billing_reports,
        unique_drivers,
        order_id,
        expected,
        billing,
):
    billing_reports.add_journal_entries(
        order_id, load_json(billing) if isinstance(billing, str) else billing,
    )
    unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': order_id},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )
    assert response.json() == load_json(expected)


@pytest.mark.parametrize(
    'status_code,is_response_with_msg', [(429, False), (429, True)],
)
@pytest.mark.now('2019-12-5T00:00:00Z')
async def test_driver_money_order_billing_429(
        taxi_driver_money,
        mocked_time,
        driver_orders,
        driver_metrics_storage,
        geotracks,
        billing_reports,
        unique_drivers,
        status_code,
        is_response_with_msg,
):
    billing_reports.set_journal_by_tag_429(is_response_with_msg)

    unique_drivers.set_unique(PARK_ID, DRIVER_ID, UNIQUE_DRIVER_ID)
    response = await taxi_driver_money.get(
        URL_V2,
        params={'park_id': PARK_ID, 'id': 'yandex'},
        headers={
            'User-Agent': 'Taximeter 9.17 (228)',
            'Accept-Language': 'ru',
            'X-Driver-Session': SESSION,
            'X-Request-Application-Version': '9.17',
            'X-YaTaxi-Park-Id': PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
        },
    )
    assert response.status_code == status_code
