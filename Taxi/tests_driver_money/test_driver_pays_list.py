import pytest


@pytest.fixture(name='parks_request_driver_pays', autouse=True)
def parks_request_driver_pays(mockserver, load_json):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        return load_json('parks_driver_profiles_list.json')


@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver_uuid1',
)
@pytest.mark.now('2020-03-23T14:34:57.623791+00:00')
@pytest.mark.parametrize(
    'category_id,group',
    [
        ('card', 'Оплата'),
        ('corporate', 'Оплата'),
        ('tip', 'Чаевые'),
        ('promotion_discount', 'Субсидия'),
        ('bonus', 'Субсидия'),
        ('platform_ride_fee', 'Комиссия'),
        ('platform_ride_vat', 'Комиссия'),
        ('platform_bonus_fee', 'Комиссия'),
        ('partner_ride_fee', 'Комиссия'),
        ('partner_bonus_fee', 'Комиссия'),
        ('bank_payment', 'Транзакция'),
        ('platform_other_referral', 'Субсидия'),
        ('partner_service_recurrent_payment', 'Списание'),
        ('another', 'Прочее'),
    ],
)
async def test_billing_response_group_category(
        taxi_driver_money,
        driver_authorizer,
        mockserver,
        fleet_transactions_api,
        category_id,
        group,
        load_json,
        driver_orders,
):
    group_code_mapping = {
        'Оплата': 4,
        'Чаевые': 3,
        'Субсидия': 7,
        'Транзакция': 1,
        'Комиссия': 2,
        'Списание': 10,
        'Прочее': 0,
    }

    fleet_transactions_api.set_folder('')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _mock_transactions_list(request):
        assert request.json['query']['park']['id'] == 'driver_db_id1'
        assert (
            request.json['query']['park']['driver_profile']['id']
            == 'driver_uuid1'
        )
        return {
            'limit': 100,
            'cursor': 'Hello',
            'transactions': [
                {
                    'id': 'trans_id1',
                    'event_at': '2020-03-23T14:34:57.623791+00:00',
                    'category_id': category_id,
                    'category_name': 'Платежи',
                    'amount': '4000.3401',
                    'currency_code': 'RUB',
                    'description': 'Описание',
                    'created_by': {'identity': 'platform'},
                    'order_id': 'alias_id_2',
                },
            ],
        }

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()['detais'][0]['group'] == group_code_mapping[group]


@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver_uuid1',
)
@pytest.mark.now('2020-03-23T14:34:57.623791+00:00')
async def test_billing_response_merging_vats(
        taxi_driver_money,
        driver_authorizer,
        mockserver,
        fleet_transactions_api,
        load_json,
        driver_orders,
):
    fleet_transactions_api.set_folder('')

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()['detais'] == load_json('fta_detais_merged.json')


@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver_uuid1',
)
@pytest.mark.parametrize('page,limit', [(0, 40), (1, 100), (2, 200), (3, 300)])
async def test_pages_sent(
        taxi_driver_money,
        driver_authorizer,
        mockserver,
        fleet_transactions_api,
        load_json,
        driver_orders,
        page,
        limit,
):
    fleet_transactions_api.set_folder('')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _mock_transactions_list(request):
        assert request.json['limit'] == limit
        return {'cursor': '', 'limit': limit, 'transactions': []}

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
        data={'page': page},
    )
    assert response.status_code == 200, response.text


@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver_uuid1',
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='instant_payouts_ios',
    consumers=['driver_money/v1_driver_pays_list'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'instant_payouts_status',
    [
        'not_available',
        'ready',
        'already_in_progress',
        'not_enough_funds',
        'daily_limit_exceeded',
        'wrong_amount',
    ],
)
async def test_instant_payouts_status(
        taxi_driver_money,
        driver_authorizer,
        mockserver,
        fleet_transactions_api,
        load_json,
        driver_orders,
        instant_payouts_status,
):

    fleet_transactions_api.set_folder('')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _mock_transactions_list(request):
        return {
            'limit': 100,
            'cursor': 'Hello',
            'transactions': [
                {
                    'id': 'trans_id1',
                    'event_at': '2020-03-23T14:34:57.623791+00:00',
                    'category_id': 'card',
                    'category_name': 'Платежи',
                    'amount': '4000.3401',
                    'currency_code': 'RUB',
                    'description': 'Описание',
                    'created_by': {'identity': 'platform'},
                    'order_id': 'alias_id_2',
                },
            ],
        }

    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/options',
    )
    def _mock_instant_payouts_options(request):
        return {
            'status': instant_payouts_status,
            'amount_minimum': '0',
            'amount_maximum': '0',
            'fee_percent': '0',
            'fee_minimum': '0',
        }

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()['instant_payouts_status'] == instant_payouts_status


@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver_uuid1',
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='balance_reports_vat',
    consumers=['driver-money/context'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
async def test_balance_reports_vat(
        taxi_driver_money,
        driver_authorizer,
        mockserver,
        fleet_transactions_api,
        load_json,
        driver_orders,
):

    fleet_transactions_api.set_folder('')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _mock_transactions_list(request):
        return {
            'limit': 100,
            'cursor': 'Hello',
            'transactions': [
                {
                    'id': 'trans_id1',
                    'event_at': '2020-03-23T14:34:57.623791+00:00',
                    'category_id': 'card',
                    'category_name': 'Платежи',
                    'amount': '4000.3401',
                    'currency_code': 'RUB',
                    'description': 'Описание',
                    'created_by': {'identity': 'platform'},
                    'order_id': 'alias_id_2',
                },
            ],
        }

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()['balance_reports_vat_enabled']


@pytest.mark.parametrize(
    'transactions_429, balances_429',
    [(True, False), (False, True), (True, True)],
)
async def test_429(
        taxi_driver_money,
        fleet_transactions_api,
        transactions_429,
        balances_429,
):
    fleet_transactions_api.set_folder('')
    if transactions_429:
        fleet_transactions_api.set_transactions_list_429()
    if balances_429:
        fleet_transactions_api.set_balances_list_429()

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
        },
    )
    assert response.status_code == 429


@pytest.mark.now('2020-03-23T14:34:57.623791+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_on_demand_payouts',
    consumers=['driver-money/context'],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'on_demand_available, payout_mode, pending_payment',
    [
        (True, 'on_demand', None),
        (True, 'on_demand', {'status': 'created'}),
        (
            True,
            'on_demand',
            {'status': 'pending', 'amount': '300', 'currency': 'RUB'},
        ),
        (False, 'on_demand', None),
        (True, 'regular', None),
        (
            True,
            'regular',
            {'status': 'pending', 'amount': '300', 'currency': 'RUB'},
        ),
    ],
)
@pytest.mark.driver_session(
    park_id='driver_db_id1', session='driver_session1', uuid='driver',
)
async def test_on_demand_payouts_ui(
        on_demand_available,
        payout_mode,
        pending_payment,
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        billing_reports,
        fleet_transactions_api,
):

    fleet_transactions_api.set_folder('')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _mock_transactions_list(request):
        return {'limit': 100, 'cursor': 'Hello', 'transactions': []}

    @mockserver.json_handler(
        '/fleet-payouts/internal/on-demand-payouts/v1/status',
    )
    def _mock_fleet_payouts(request):
        result = {
            'payout_mode': payout_mode,
            'payout_scheduled_at': '2020-01-26T10:00:00+00:00',
            'on_demand_available': on_demand_available,
        }
        if pending_payment:
            result.update({'pending_payment': pending_payment})
        return result

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    def _mock_payments(request):
        return {'payments': [], 'cursor': {}}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        resp = load_json('parks_driver_profiles_list.json')
        resp['parks'][0]['driver_partner_source'] = 'self_employed'
        resp['parks'][0]['provider_config'] = {'yandex': {'clid': 'clid'}}
        return resp

    def get_expected_icon_detail(pending_payment):
        result = {
            'left_icon': {'icon_type': 'flip'},
            'title': 'Обрабатываем выплату',
            'type': 'icon_detail',
        }
        if pending_payment['status'] == 'pending':
            result.update(
                {'title': 'Банк готовит перевод', 'detail': '300,00 ₽'},
            )
        return result

    response = await taxi_driver_money.post(
        '/v1/driver/pays/list',
        params={'park_id': 'driver_db_id1'},
        headers={
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter 9.28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Application-Version': '9.28',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == 200

    on_demand_payout_info = response.json()['on_demand_payout_info']
    if payout_mode == 'on_demand':
        ui_ = on_demand_payout_info['ui']
        button_index = 0
        if pending_payment is not None:
            button_index = 1
            icon_detail = ui_[0]
            assert icon_detail == get_expected_icon_detail(pending_payment)
        button = ui_[button_index]
        assert button == {
            'accent': True,
            'enabled': on_demand_available,
            'horizontal_divider_type': 'none',
            'payload': {'type': 'navigate_to_payout'},
            'title': 'Запросить вывод денег',
            'type': 'button',
        }
    else:
        assert 'ui' not in on_demand_payout_info
