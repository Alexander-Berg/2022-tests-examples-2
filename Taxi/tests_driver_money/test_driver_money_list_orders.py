import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,limit,before,timezone,billing_balance_response,expected',
    [
        pytest.param(
            'day',
            20,
            None,
            'Asia/Tbilisi',
            'billing_balances_response_daily.json',
            'expected_response_day.json',
            id='day',
        ),
        pytest.param(
            'week',
            3,
            None,
            '-05:00',
            'billing_balances_response.json',
            'expected_response_week.json',
            id='week',
        ),
        pytest.param(
            'month',
            20,
            None,
            'Europe/Moscow',
            'billing_balances_response_month.json',
            'expected_response_month.json',
            id='month',
        ),
        pytest.param(
            'week',
            3,
            '2019-05-13T00:00:00',
            '-05:00',
            'billing_balances_response.json',
            'expected_response_week_limit2.json',
            id='limit',
            marks=[pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=2)],
        ),
    ],
)
async def test_driver_money_list_orders(
        taxi_driver_money,
        billing_reports,
        load_json,
        group_by,
        limit,
        before,
        timezone,
        billing_balance_response,
        expected,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )
    billing_reports.set_balances(load_json(billing_balance_response))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'limit': limit,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/orders',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert load_json(expected) == response.json()


@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_driver_money_list_orders_pagination(
        taxi_driver_money, billing_reports, load_json, billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )
    billing_reports.set_balances(
        load_json('billing_balances_response_month.json'),
    )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': 'month',
        'limit': 6,
        'tz': 'Europe/Moscow',
    }
    for page_no in range(1, 4):
        response = await taxi_driver_money.get(
            'v1/driver/money/list/orders',
            params=params,
            headers={
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': 'park_id_0',
                'X-YaTaxi-Driver-Profile-Id': 'driver',
            },
        )
        assert response.status_code == 200
        assert (
            load_json(f'expected_response_page_{page_no}.json')
            == response.json()
        )
        if page_no != 3:
            params['before'] = response.json()['last_date']


@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_driver_money_list_orders_correct_header(
        taxi_driver_money, billing_reports, load_json, billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )
    billing_reports.set_balances(
        load_json('billing_balances_response_month.json'),
    )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': 'month',
        'limit': 1,
        'tz': 'Europe/Moscow',
    }

    response = await taxi_driver_money.get(
        'v1/driver/money/list/orders',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert (
        load_json('expected_response_correct_header.json') == response.json()
    )


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            'expected_response_day_fully_paid.json',
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_enable_full_paid_history.json',
                ),
                pytest.mark.config(
                    DRIVER_MONEY_ISCLOSE_BY_CURRENCY={
                        '__default__': {
                            'relative_tolerance': 0,
                            'absolute_tolerance': 0,
                        },
                        'RUB': {
                            'relative_tolerance': 0,
                            'absolute_tolerance': 0.01,
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_driver_money_list_orders_fully_paid(
        taxi_driver_money,
        mockserver,
        load_json,
        billing_reports,
        expected,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        return load_json('billing_parks_payments_orders_response.json')

    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': 'day',
        'limit': 20,
        'tz': 'Asia/Tbilisi',
    }

    response = await taxi_driver_money.get(
        'v1/driver/money/list/orders',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert load_json(expected) == response.json()


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.experiments3(
    filename='experiments3_enable_full_paid_history.json',
)
@pytest.mark.config(
    DRIVER_MONEY_ISCLOSE_BY_CURRENCY={
        '__default__': {'relative_tolerance': 0, 'absolute_tolerance': 0},
        'RUB': {'relative_tolerance': 0, 'absolute_tolerance': 0.01},
    },
)
@pytest.mark.parametrize(
    'fallback_fired, billing_bank_orders_ok, expected',
    [
        pytest.param(True, True, 'expected_response_day_fully_paid_2.json'),
        pytest.param(True, False, 'expected_response_day_fully_paid_2.json'),
        pytest.param(False, False, 'expected_response_day_fully_paid_2.json'),
        pytest.param(False, True, 'expected_response_day_fully_paid.json'),
    ],
)
async def test_driver_money_list_orders_fully_paid_stats(
        taxi_driver_money,
        mockserver,
        statistics,
        load_json,
        billing_reports,
        fallback_fired,
        billing_bank_orders_ok,
        expected,
        billing_subventions_x,
):
    metric_prefix = (
        'handler.billing-bank-orders./v1/parks/payments/orders-post'
    )

    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        if billing_bank_orders_ok:
            return load_json('billing_parks_payments_orders_response.json')
        return mockserver.make_response(status=500)

    if fallback_fired:
        statistics.fallbacks = [f'{metric_prefix}.fallback']
    await taxi_driver_money.invalidate_caches()

    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': 'day',
        'limit': 20,
        'tz': 'Asia/Tbilisi',
    }

    async with statistics.capture(taxi_driver_money) as capture:
        response = await taxi_driver_money.get(
            'v1/driver/money/list/orders',
            params=params,
            headers={
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': 'park_id_0',
                'X-YaTaxi-Driver-Profile-Id': 'driver',
            },
        )

    if not billing_bank_orders_ok and not fallback_fired:
        assert response.status_code == 500
        return

    assert response.status_code == 200
    assert load_json(expected) == response.json()
    if fallback_fired:
        assert not capture.statistics.get(f'{metric_prefix}.success')
        assert not capture.statistics.get(f'{metric_prefix}.error')
    elif billing_bank_orders_ok:
        assert capture.statistics.get(f'{metric_prefix}.success') == 1
    else:
        assert capture.statistics.get(f'{metric_prefix}.error') == 1
