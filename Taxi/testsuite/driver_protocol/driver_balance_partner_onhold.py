import json

import pytest

URL = 'driver/balance/partner-onhold'

PARK_ID = 'parkForBalance'
DRIVER_ID = 'driverForBalance'
SESSION = 'sess'

AUTH_DATA = {'db': PARK_ID, 'session': SESSION}

HANDLER_DATA = {'end_time': '2019-06-10T12:00:00.000Z', 'limit': 8}

HEADERS = {'Accept-Language': 'en', 'User-Agent': 'Taximeter 8.88 (1234)'}

ADDRESS_1 = {'Street': 'ADDRESS'}

ADDRESS_2 = {'Street': 'ADDRESS', 'House': '2b7'}


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
def test_balance_onhold_screen(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        load,
):
    driver_authorizer_service.set_session(PARK_ID, SESSION, DRIVER_ID)

    @mockserver.json_handler('/billing_reports/v1/journal/select')
    def pp_list(request):
        return mockserver.make_response(load('payments.json'), status=200)

    @mockserver.json_handler('/billing_reports/v1/balances/select')
    def balances_list(request):
        return mockserver.make_response(load('balances.json'), status=200)

    response = taxi_driver_protocol.post(
        URL, params=AUTH_DATA, json=HANDLER_DATA, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('onhold_screen.json')
