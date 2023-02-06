import pytest

from order_notify.repositories.order_info import OrderData


REQUESTS = [
    {
        'source': {
            'geopoint': [2.340111, 48.855311],
            'fullname': 'Франция, Париж',
        },
    },
    {
        'source': {
            'geopoint': [37.5386034054134, 55.75061257901266],
            'fullname': 'Россия, Москва',
        },
    },
]


STATUS_UPDATES = [
    {'c': {'$date': 1638957444566}},
    {
        'c': {'$date': 1638957450057},
        'p': {'taxi_status': 'pending', 'geopoint': [37.532645, 55.755168]},
    },
    {
        'p': {'taxi_status': 'driving', 'geopoint': [37.532645, 55.755168]},
        'c': {'$date': 1638957450490},
    },
    {
        'p': {'taxi_status': 'waiting', 'geopoint': [37.538678, 55.750472]},
        'c': {'$date': 1638957558590},
    },
    {
        'p': {
            'taxi_status': 'transporting',
            'geopoint': [37.538549, 55.750594],
        },
        'c': {'$date': 1638957575991},
    },
    {
        'p': {'taxi_status': 'complete', 'geopoint': [37.534818, 55.750515]},
        'c': {'$date': 1638957675660},
    },
]


DEFAULT_ORDER_DATA = OrderData(
    brand='',
    country='',
    order={},
    order_proc={
        'order_info': {'statistics': {'status_updates': STATUS_UPDATES}},
    },
)


@pytest.mark.parametrize(
    'order_data, expected_application',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'order': {'application': 'android'}},
            ),
            'android',
            id='android',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'order': {'application': 'yataxi'}},
            ),
            'yataxi',
            id='yataxi',
        ),
    ],
)
def test_get_application(order_data, expected_application):
    application = order_data.get_application()
    assert application == expected_application


@pytest.mark.parametrize(
    'order_data, expected_request',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'order': {'request': REQUESTS[0]}},
            ),
            REQUESTS[0],
            id='order_proc_request',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={'request': REQUESTS[1]},
                order_proc={'order': {}},
            ),
            REQUESTS[1],
            id='order_request',
        ),
    ],
)
def test_get_request(order_data, expected_request):
    request = order_data.get_request()
    assert request == expected_request


@pytest.mark.parametrize(
    'order_data, expected_status_updates',
    [
        pytest.param(
            OrderData(
                brand='', country='', order={}, order_proc={'order_info': {}},
            ),
            [],
            id='empty',
        ),
        pytest.param(DEFAULT_ORDER_DATA, STATUS_UPDATES, id='exists'),
    ],
)
def test_get_status_updates(order_data, expected_status_updates):
    status_updates = order_data.get_status_updates()
    assert status_updates == expected_status_updates


@pytest.mark.parametrize(
    'order_data, expected_start_transporting_time',
    [
        pytest.param(
            OrderData(
                brand='', country='', order={}, order_proc={'order_info': {}},
            ),
            None,
            id='empty',
        ),
        pytest.param(
            DEFAULT_ORDER_DATA, {'$date': 1638957575991}, id='exists',
        ),
    ],
)
def test_get_start_transporting_time(
        order_data, expected_start_transporting_time,
):
    start_transporting_time = order_data.get_start_transporting_time()
    assert start_transporting_time == expected_start_transporting_time


@pytest.mark.parametrize(
    'order_data, expected_complete_time',
    [
        pytest.param(
            OrderData(
                brand='', country='', order={}, order_proc={'order_info': {}},
            ),
            None,
            id='empty',
        ),
        pytest.param(
            DEFAULT_ORDER_DATA, {'$date': 1638957675660}, id='exists',
        ),
    ],
)
def test_get_complete_time(order_data, expected_complete_time):
    start_transporting_time = order_data.get_complete_time()
    assert start_transporting_time == expected_complete_time


def test_get_driver_id():
    expected_driver_id = 'a35339fb465a43c392b5501588d299b5'
    order_data = OrderData(
        brand='',
        country='',
        order={},
        order_proc={'performer': {'driver_id': f'643_{expected_driver_id}'}},
    )
    driver_id = order_data.get_driver_id()
    assert driver_id == expected_driver_id


@pytest.mark.parametrize(
    'order_data, expected_credit_card',
    [
        pytest.param(
            OrderData(brand='', country='', order={}, order_proc={}),
            None,
            id='empty',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={'creditcard': {'code': 2323}},
                order_proc={},
            ),
            {'code': 2323},
            id='exists',
        ),
    ],
)
def test_get_credit_card(order_data, expected_credit_card):
    credit_card = order_data.get_credit_card()
    assert credit_card == expected_credit_card


@pytest.mark.parametrize(
    'order_data, expected_used_payment_id',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={'payment_tech': {'main_card_payment_id': '1'}},
                order_proc={},
            ),
            '1',
            id='no_billing_tech',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={
                    'payment_tech': {'main_card_payment_id': '2'},
                    'billing_tech': {},
                },
                order_proc={},
            ),
            '2',
            id='no_transactions',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={
                    'payment_tech': {'main_card_payment_id': '2'},
                    'billing_tech': {'transactions': []},
                },
                order_proc={},
            ),
            '2',
            id='empty_transactions',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={
                    'payment_tech': {'main_card_payment_id': '3'},
                    'billing_tech': {
                        'transactions': [{'card_payment_id': '1'}],
                    },
                },
                order_proc={},
            ),
            '1',
            id='one_transaction',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={
                    'payment_tech': {'main_card_payment_id': '3'},
                    'billing_tech': {
                        'transactions': [
                            {'card_payment_id': '1'},
                            {'card_payment_id': '2'},
                        ],
                    },
                },
                order_proc={},
            ),
            '2',
            id='two_transactions',
        ),
    ],
)
def test_get_used_payment_id(order_data, expected_used_payment_id):
    used_payment_id = order_data.get_used_payment_id()
    assert used_payment_id == expected_used_payment_id


@pytest.mark.parametrize(
    'order_proc, expected_candidate',
    [
        pytest.param({}, None, id='no_performer'),
        pytest.param({'performer': {}}, None, id='no_candidate_index'),
        pytest.param(
            {
                'candidates': [{'_id': 'ghjk'}],
                'performer': {'candidate_index': 0},
            },
            {'_id': 'ghjk'},
            id='exist_candidate',
        ),
    ],
)
def test_get_chosen_candidate(order_proc, expected_candidate):
    order_data = OrderData(
        brand='', country='', order={}, order_proc=order_proc,
    )
    candidate = order_data.get_chosen_candidate()
    assert candidate == expected_candidate
