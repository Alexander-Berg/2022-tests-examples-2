import json

import pytest

URL = 'driver/balance/partner-main'

PARK_ID = 'parkForBalance'
DRIVER_ID = 'driverForBalance'
SESSION = 'sess'
PARK_ID_EUR = 'parkForBalanceEUR'
DRIVER_ID_EUR = 'driverForBalanceEUR'

AUTH_DATA = {'db': PARK_ID, 'session': SESSION}

AUTH_DATA_EUR = {'db': PARK_ID_EUR, 'session': SESSION}

HANDLER_DATA = {'end_time': '2019-06-05T12:00:00.000Z', 'limit': 8}

HANDLER_DATA_SECOND_PAGE = {
    'end_time': '2019-06-05T12:00:00.000Z',
    'limit': 20,
}

BAD_HANDLER_DATA = {'end_time': '2019-06-05T12:00:00.000Z', 'limit': '20'}

BAD_INPUT_ERROR = {'error': {'text': 'Bad request data format'}}

HEADERS = {'Accept-Language': 'en', 'User-Agent': 'Taximeter 8.88 (1234)'}

ADDRESS_1 = {'Street': 'ADDRESS'}

ADDRESS_2 = {'Street': 'ADDRESS', 'House': '2b7'}


def test_balance_partner_bad_input(
        taxi_driver_protocol, driver_authorizer_service,
):

    driver_authorizer_service.set_session(PARK_ID, SESSION, DRIVER_ID)

    response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=BAD_HANDLER_DATA, headers=HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == BAD_INPUT_ERROR


@pytest.mark.driver_experiments('onhold_partner_v2')
@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (id, park_id, address_from, number, '
    'date_create, date_booking) '
    'VALUES (\'{order_id}\', \'{park_id}\', \'{address_from}\', {number}, '
    'now(), now())'.format(
        order_id='order1',
        park_id=PARK_ID,
        address_from=json.dumps(ADDRESS_1),
        number=12,
    ),
    'INSERT INTO orders_0 (id, park_id, address_from, number, '
    'date_create, date_booking) '
    'VALUES (\'{order_id}\', \'{park_id}\', \'{address_from}\', {number}, '
    'now(), now())'.format(
        order_id='order2',
        park_id=PARK_ID,
        address_from=json.dumps(ADDRESS_2),
        number=17,
    ),
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'billing_subventions'}],
    TVM_SERVICES={'driver_protocol': 1, 'billing-reports': 2},
)
def test_balance_partner_main_screen(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        tvm2_client,
        load_json,
        load,
):

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'2': {'ticket': ticket}}))

    driver_authorizer_service.set_session(PARK_ID, SESSION, DRIVER_ID)

    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select(request):
        req = json.loads(request.data)
        if 'cursor' not in req or req['cursor'] == {}:
            return mockserver.make_response(load('payments.json'), status=200)

        elif req['cursor'] == {'1': '1'}:
            return mockserver.make_response(
                load('payments_add.json'), status=200,
            )
        elif req['cursor'] == {'2': '2'}:
            return mockserver.make_response(
                load('payments_second.json'), status=200,
            )
        else:
            return mockserver.make_response(
                load('payments_empty_cursor.json'), status=200,
            )

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_select(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        return mockserver.make_response(load('balances.json'), status=200)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_driver_profiles_search(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'driver_profiles': [
                        {
                            'driver_profile': {},
                            'accounts': [
                                {'id': 'driverForBalance', 'balance': '7777'},
                            ],
                        },
                    ],
                    'parks': [],
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=HANDLER_DATA, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('main_screen.json')

    HANDLER_DATA_SECOND_PAGE = dict(HANDLER_DATA)
    end_time = response.json()['ui']['primary']['last_item_date']
    HANDLER_DATA_SECOND_PAGE['end_time'] = end_time
    cursor = response.json()['ui']['primary']['cursor']
    HANDLER_DATA_SECOND_PAGE['cursor'] = cursor

    second_response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=HANDLER_DATA_SECOND_PAGE, headers=HEADERS,
    )

    assert second_response.status_code == 200
    assert second_response.json() == load_json('main_screen_second.json')


@pytest.mark.driver_experiments('onhold_partner_v2')
def test_armenia_commission(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        load,
):
    driver_authorizer_service.set_session('parkAM', SESSION, 'driverAM')

    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select(request):
        req = json.loads(request.data)
        if 'cursor' not in req or req['cursor'] == {}:
            return mockserver.make_response(
                load('Armenia_payments.json'), status=200,
            )
        else:
            return mockserver.make_response(
                load('payments_empty_cursor.json'), status=200,
            )

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_select(request):
        return mockserver.make_response(
            load('Armenia_balances.json'), status=200,
        )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_driver_profiles_search(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'driver_profiles': [
                        {
                            'driver_profile': {},
                            'accounts': [
                                {'id': 'driverForBalance', 'balance': '7777'},
                            ],
                        },
                    ],
                    'parks': [],
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.post(
        URL,
        params={'db': 'parkAM', 'session': SESSION},
        json=HANDLER_DATA,
        headers={
            'Accept-Language': 'hy',
            'User-Agent': 'Taximeter 8.88 (1234)',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('Armenia_screen.json')


def test_balance_negative_zero_rub(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        load,
):

    driver_authorizer_service.set_session(PARK_ID, SESSION, DRIVER_ID)

    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select(request):
        return mockserver.make_response(
            load('payments_empty.json'), status=200,
        )

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_select(request):
        return mockserver.make_response('[]', status=200)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_driver_profiles_search(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'driver_profiles': [
                        {
                            'driver_profile': {},
                            'accounts': [
                                {
                                    'id': 'driverForBalance',
                                    'balance': '-0.273',
                                },
                            ],
                        },
                    ],
                    'parks': [],
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.post(
        URL,
        params=AUTH_DATA,
        json=HANDLER_DATA,  # minus 3 years in zero_balance_screen.json
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('zero_balance_screen_rub.json')


@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        'EUR': {'__default__': 1},
        '__default__': {'__default__': 0},
    },
)
def test_balance_negative_zero_eur(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        load,
):

    driver_authorizer_service.set_session(PARK_ID_EUR, SESSION, DRIVER_ID_EUR)

    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select(request):
        return mockserver.make_response(
            load('payments_empty.json'), status=200,
        )

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_select(request):
        return mockserver.make_response('[]', status=200)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_driver_profiles_search(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'driver_profiles': [
                        {
                            'driver_profile': {},
                            'accounts': [
                                {
                                    'id': 'driverForBalance',
                                    'balance': '-0.0495',
                                },
                            ],
                        },
                    ],
                    'parks': [],
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.post(
        URL,
        params=AUTH_DATA_EUR,
        json=HANDLER_DATA,  # minus 3 years in zero_balance_screen.json
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('zero_balance_screen_eur.json')


def test_balance_too_many_requests(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        load,
):

    driver_authorizer_service.set_session(PARK_ID, SESSION, DRIVER_ID)

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_select(request):
        return mockserver.make_response('[]', status=200)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_driver_profiles_search(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'driver_profiles': [
                        {
                            'driver_profile': {},
                            'accounts': [
                                {
                                    'id': 'driverForBalance',
                                    'balance': '-0.0495',
                                },
                            ],
                        },
                    ],
                    'parks': [],
                },
            ),
            status=200,
        )

    # 429 remains
    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select(request):
        return mockserver.make_response('{}', status=429)

    response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=HANDLER_DATA, headers=HEADERS,
    )

    assert response.status_code == 429

    # other 4xx become 500
    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def journal_select_2(request):
        return mockserver.make_response({}, status=418)

    response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=HANDLER_DATA, headers=HEADERS,
    )

    assert response.status_code == 500
