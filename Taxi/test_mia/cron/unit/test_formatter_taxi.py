# pylint: disable=protected-access
import pytest

from mia.crontasks.extra_fetcher import extra_fetcher_taxi
from mia.crontasks.formatter import formatter_taxi


FORMATTER = formatter_taxi.FormatterTaxi()

_CHAT_UPDATES = [
    {
        'chat_id': 'chat_id_2',
        'update_id': 'update_2',
        'data': {
            'created_date': '2020-01-01T00:00:01.000000Z',
            'message': {'sender': {'role': 'driver'}, 'text': 'text 2'},
        },
    },
    {
        'chat_id': 'chat_id_2',
        'update_id': 'update_1',
        'data': {
            'created_date': '2020-01-01T00:00:00.000000Z',
            'message': {'sender': {'role': 'driver'}, 'text': 'text 1'},
        },
    },
]

_CHAT_TRANSLATIONS = [
    {'chat_id': 'chat_id_2', 'update_id': 'update_1', 'text': 'translation 1'},
    {'chat_id': 'chat_id_2', 'update_id': 'update_2', 'text': 'translation 2'},
]


@pytest.mark.parametrize(
    'data, expected',
    [
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {
                    'order_id': 'test_order_id',
                    'created': 1551420131.582,
                    'request_due': 1551424321.012,
                    'request_source': {
                        'fullname': 'test_request_source',
                        'geopoint': [1, 1],
                        'contact_phone': 'test_phone_1',
                    },
                    'request_destinations': [
                        {
                            'fullname': 'destination_1',
                            'geopoint': [1, 2],
                            'contact_phone': 'test_phone_2',
                        },
                        {
                            'fullname': 'destination_2',
                            'geopoint': [2, 3],
                            'contact_phone': 'test_phone_3',
                        },
                        {'fullname': 'destination_3', 'geopoint': [3, 4]},
                    ],
                    'user_phone_id': 'id_3_2',
                    'user_phone': 'test_phone_3',
                    'extra_user_phone': 'test_phone_4',
                },
                {
                    'performer_taxi_alias_id': 'test_performer_taxi_alias_id',
                    'statistics': {
                        'complete_time': 1551125221.012,
                        'cancel_time': 256.123,
                    },
                    'feedback': {
                        'choices': {
                            'cancelled_reason': ['test_cancelled_reason'],
                        },
                    },
                    'cost': 231,
                    'payment_tech_type': 'corp',
                    'request_source': {'geopoint': [12.34, 98.76]},
                    'request_destinations': [
                        {'geopoint': [1, 2]},
                        {'geopoint': [2, 3]},
                    ],
                    'status': 'finished',
                    'taxi_status': 'complete',
                    'order_events': [
                        {
                            'name': 'status_update',
                            'value': {
                                'status': 'finished',
                                'position': {'geopoint': [1.1, 1.1]},
                            },
                        },
                        {
                            'name': 'status_update',
                            'value': {
                                'status': 'finished',
                                'position': {'geopoint': [2.2]},
                            },
                        },
                        {
                            'name': 'status_update',
                            'value': {
                                'status': 'finished',
                                'position': {'geopoint': None},
                            },
                        },
                        {
                            'name': 'status_update',
                            'value': {'status': 'some_status'},
                        },
                        {'name': 'some_name'},
                    ],
                },
                {},
                {},
                'Europe/Moscow',
                _CHAT_UPDATES,
                _CHAT_TRANSLATIONS,
            ),
            {
                'order_id': 'test_order_id',
                'created_time': '01.03.2019 09:02:11+0300',
                'request_due': '01.03.2019 10:12:01+0300',
                'order_id_for_partners': 'test_performer_taxi_alias_id',
                'finished_time': '25.02.2019 23:07:01+0300',
                'cost': 231,
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'middle_destinations': [
                    'destination_1 | точка отправления: (2, 1)',
                    'destination_2 | точка отправления: (3, 2)',
                ],
                'payment_method': 'корпоративный заказ',
                'cancellation_reason': 'test_cancelled_reason',
                'from': ('test_request_source | точка отправления: ' '(1, 1)'),
                'to': 'destination_3 | точка отправления: (3, 2)',
                'is_completed': True,
                'passenger_phone': 'test_phone_4',
                'user_phone': 'test_phone_3',
                'source_contact_phone': 'test_phone_1',
                'destination_contact_phones': ['test_phone_2', 'test_phone_3'],
                'arrival_point': (1.1, 1.1),
                'canceled_time': '01.03.2019 09:06:27+0300',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'chat': [
                    {
                        'author': 'driver',
                        'created_date': '01.01.2020 03:00:00+0300',
                        'text': 'text 1',
                        'translation': 'translation 1',
                    },
                    {
                        'author': 'driver',
                        'created_date': '01.01.2020 03:00:01+0300',
                        'text': 'text 2',
                        'translation': 'translation 2',
                    },
                ],
            },
        ),
    ],
)
async def test_format(data, expected):
    assert await FORMATTER._format_row(data, True, True) == expected


@pytest.mark.parametrize(
    'data, dump_all_candidates, expected',
    [
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {
                    'created': 1551420131.582,
                    'candidates': [
                        {'driver_id': '1'},
                        {'driver_id': '2'},
                        {'driver_id': '3'},
                        {'driver_id': '4'},
                    ],
                },
                {},
                {},
                {},
                'Europe/Moscow',
            ),
            True,
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'candidates': [
                    {
                        'driver_phone': '',
                        'driver_name': '',
                        'driver_license': '',
                        'car_model': '',
                        'license_plates': '',
                    },
                    {
                        'driver_phone': '',
                        'driver_name': '',
                        'driver_license': '',
                        'car_model': '',
                        'license_plates': '',
                    },
                    {
                        'driver_phone': '',
                        'driver_name': '',
                        'driver_license': '',
                        'car_model': '',
                        'license_plates': '',
                    },
                    {
                        'driver_phone': '',
                        'driver_name': '',
                        'driver_license': '',
                        'car_model': '',
                        'license_plates': '',
                    },
                ],
                'from': '-',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'middle_destinations': [],
                'payment_time': '-',
                'is_completed': False,
            },
        ),
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {
                    'created': 1551420131.582,
                    'candidates': [
                        {'driver_id': '1'},
                        {'driver_id': '2'},
                        {
                            'driver_id': '3',
                            'driver_name': 'test_driver_name_3',
                        },
                        {'driver_id': '4'},
                    ],
                    'performer_driver_id': '3',
                },
                {},
                {},
                {},
                'Europe/Moscow',
            ),
            False,
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'driver_id': '3',
                'driver_name': 'test_driver_name_3',
                'from': '-',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'middle_destinations': [],
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'is_completed': False,
            },
        ),
    ],
)
async def test_format_candidates(data, dump_all_candidates, expected):
    assert (
        await FORMATTER._format_row(data, dump_all_candidates, False)
        == expected
    )


@pytest.mark.parametrize(
    'data, expected',
    [
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {'created': 1551420131.582},
                {},
                {'junk': 1},
                {},
                'Europe/Moscow',
            ),
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'middle_destinations': [],
                'from': '-',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'is_completed': False,
            },
        ),
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {'created': 1551420131.582},
                {},
                {
                    'id': 'test_park_id',
                    'name': 'test_park_name',
                    'phone': 'test_park_phone',
                },
                {},
                'Europe/Moscow',
            ),
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': 'test_park_name',
                'park_phone': 'test_park_phone',
                'middle_destinations': [],
                'from': '-',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'is_completed': False,
            },
        ),
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {'created': 1551420131.582},
                {},
                {
                    'id': 'test_park_id',
                    'name': 'test_park_name',
                    'phone': 'test_park_phone',
                },
                {
                    'id': 'test_pda_park_id_1',
                    'name': 'test_pda_name_1',
                    'contacts': None,
                },
                'Europe/Moscow',
            ),
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': 'test_park_name',
                'park_phone': 'test_park_phone',
                'middle_destinations': [],
                'from': '-',
                'masked_pan': '-',
                'payment_time': '-',
                'rrn': '-',
                'approval_code': '-',
                'is_completed': False,
            },
        ),
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {'created': 1551420131.582},
                {},
                {
                    'id': 'test_park_id',
                    'name': 'test_park_name',
                    'phone': 'test_park_phone',
                },
                {
                    'id': 'test_pda_park_id_1',
                    'name': 'test_pda_name_1',
                    'contacts': {},
                },
                'Europe/Moscow',
            ),
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': 'test_park_name',
                'park_phone': 'test_park_phone',
                'middle_destinations': [],
                'from': '-',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'is_completed': False,
            },
        ),
        (
            extra_fetcher_taxi.RowWithExtraTaxi(
                {'created': 1551420131.582},
                {},
                {
                    'id': 'test_park_id',
                    'name': 'test_park_name',
                    'phone': 'test_park_phone',
                },
                {
                    'id': 'test_pda_park_id_1',
                    'name': 'test_pda_name_1',
                    'contacts': {
                        'contact_1': {'not_phones': 'stub'},
                        'contact_2': {'phones': 'test_contacts_phones_1'},
                    },
                },
                'Europe/Moscow',
            ),
            {
                'created_time': '01.03.2019 09:02:11+0300',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': 'test_park_name',
                'park_phone': 'test_park_phone',
                'middle_destinations': [],
                'from': '-',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'is_completed': False,
            },
        ),
    ],
)
async def test_format_park(data, expected):
    assert await FORMATTER._format_row(data, True, False) == expected


@pytest.mark.parametrize(
    'candidates, expected',
    [
        (None, None),
        ([], None),
        (
            [{}],
            [
                {
                    'driver_phone': '',
                    'driver_name': '',
                    'driver_license': '',
                    'car_model': '',
                    'license_plates': '',
                },
            ],
        ),
        (
            [
                {
                    'driver_phone': 'test driver_phone 1',
                    'driver_name': 'test driver_name 1',
                    'driver_license': 'test driver_licence 1',
                    'car_model': 'test car_model 1',
                    'car_number': 'test car_number 1',
                },
                {
                    'driver_phone': 'test driver_phone 2',
                    'driver_name': 'test driver_name 2',
                    'driver_license': 'test driver_licence 2',
                    'car_model': 'test car_model 2',
                    'car_number': 'test car_number 2',
                },
            ],
            [
                {
                    'driver_phone': 'test driver_phone 1',
                    'driver_name': 'test driver_name 1',
                    'driver_license': 'test driver_licence 1',
                    'car_model': 'test car_model 1',
                    'license_plates': 'test car_number 1',
                },
                {
                    'driver_phone': 'test driver_phone 2',
                    'driver_name': 'test driver_name 2',
                    'driver_license': 'test driver_licence 2',
                    'car_model': 'test car_model 2',
                    'license_plates': 'test car_number 2',
                },
            ],
        ),
    ],
)
async def test_candidates(candidates, expected):
    assert formatter_taxi.FormatterTaxi._candidates(candidates) == expected


@pytest.mark.parametrize(
    'vals, expected',
    [
        (None, None),
        ([], None),
        (['a'], 'a'),
        (['a', 'b'], 'a, b'),
        (['a', 'b', 'c'], 'a, b, c'),
    ],
)
async def test_join(vals, expected):
    assert formatter_taxi.FormatterTaxi._join(vals) == expected


@pytest.mark.parametrize(
    'point, expected',
    [
        (None, ''),
        ([], ''),
        ([12.34], ' | точка отправления: (12.34,)'),
        ([12.34, 23.45], ' | точка отправления: (23.45, 12.34)'),
        ([12.34, 23.45, 34.56], ' | точка отправления: (34.56, 23.45, 12.34)'),
    ],
)
async def test_point_text(point, expected):
    assert formatter_taxi.FormatterTaxi._point_text(point) == expected


@pytest.mark.parametrize(
    'payment, expected',
    [
        (None, None),
        ('test_payment', 'test_payment'),
        ('cash', 'наличные'),
        ('card', 'кредитная карта'),
        ('corp', 'корпоративный заказ'),
        ('applepay', 'apple pay'),
        ('googlepay', 'google pay'),
        ('coupon', 'предоплата по ваучеру'),
        ('personal_wallet', 'личный счет'),
        ('coop_account', 'групповой счет'),
    ],
)
async def test_payment(payment, expected):
    assert formatter_taxi.FormatterTaxi._payment(payment) == expected


async def test_arrival_point_is_not_completed():
    assert FORMATTER._arrival_point(None, False) is None


@pytest.mark.parametrize(
    'order_events, expected',
    [
        (
            [
                {
                    'name': 'status_update',
                    'value': {'status': 'finished', 'position': {}},
                },
            ],
            None,
        ),
        (
            [
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': None},
                    },
                },
            ],
            None,
        ),
        (
            [
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': []},
                    },
                },
            ],
            None,
        ),
        (
            [
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [12.34]},
                    },
                },
            ],
            None,
        ),
        (
            [
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [12.34, 82.12]},
                    },
                },
            ],
            (82.12, 12.34),
        ),
        (
            [
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [12.34, 82.12, 98.52]},
                    },
                },
            ],
            (82.12, 12.34),
        ),
        (
            [
                {'name': 'some_name'},
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [1.1, 1.1]},
                    },
                },
                {'name': 'some_name'},
                {'name': 'some_name'},
                {'name': 'some_name'},
            ],
            (1.1, 1.1),
        ),
        (
            [
                {'name': 'status_update', 'value': {'status': 'some_status'}},
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [1.1, 1.1]},
                    },
                },
                {
                    'name': 'status_update',
                    'value': {
                        'status': 'finished',
                        'position': {'geopoint': [2.2, 2.2]},
                    },
                },
                {'name': 'status_update', 'value': {'status': 'some_status'}},
                {'name': 'status_update', 'value': {'status': 'some_status'}},
            ],
            (2.2, 2.2),
        ),
    ],
)
async def test_arrival_point(order_events, expected):
    assert FORMATTER._arrival_point(order_events, True) == expected


@pytest.mark.parametrize(
    'cancel_time, created_time, timezone, expected',
    [
        (None, None, None, None),
        (123456, 1570708207, 'Europe/Moscow', '12.10.2019 01:07:43+0300'),
    ],
)
async def test_canceled_time(cancel_time, created_time, timezone, expected):
    canceled_time = FORMATTER._canceled_time(
        cancel_time, created_time, timezone,
    )
    assert canceled_time == expected


@pytest.mark.parametrize(
    'destinations, order_request_destinations, expected',
    [
        (None, None, None),
        ([], None, None),
        (
            [
                {'fullname': 'destination_1', 'geopoint': [1.1, 2.2]},
                {'fullname': 'destination_2', 'geopoint': [2.2, 3.3]},
                {'fullname': 'destination_3', 'geopoint': [3.3, 4.4]},
            ],
            [],
            'destination_3',
        ),
        (
            [
                {'fullname': 'destination_1', 'geopoint': [1.1, 2.2]},
                {'fullname': 'destination_2', 'geopoint': [2.2, 3.3]},
                {'fullname': 'destination_3', 'geopoint': [3.3, 4.4]},
            ],
            [{'geopoint': [1, 2]}, {'geopoint': [2, 3]}],
            'destination_3 | точка отправления: (3, 2)',
        ),
    ],
)
async def test_to(destinations, order_request_destinations, expected):
    assert FORMATTER._to(destinations, order_request_destinations) == expected


@pytest.mark.parametrize(
    'test_case',
    [
        {'test_input': {'destinations': None}, 'expected_result': None},
        {'test_input': {'destinations': []}, 'expected_result': []},
        {
            'test_input': {
                'destinations': [
                    {'fullname': 'destination_1', 'geopoint': [1.1, 2.2]},
                ],
            },
            'expected_result': [],
        },
        {
            'test_input': {
                'destinations': [
                    {'fullname': 'destination_1', 'geopoint': [1.1, 2.2]},
                    {'fullname': 'destination_2', 'geopoint': [2.2, 3.3]},
                ],
            },
            'expected_result': [
                'destination_1 | точка отправления: (2.2, 1.1)',
            ],
        },
        {
            'test_input': {
                'destinations': [
                    {'fullname': 'destination_1', 'geopoint': [1.1, 2.2]},
                    {'fullname': 'destination_2', 'geopoint': [2.2, 3.3]},
                    {'fullname': 'destination_3', 'geopoint': [3.3, 4.4]},
                ],
            },
            'expected_result': [
                'destination_1 | точка отправления: (2.2, 1.1)',
                'destination_2 | точка отправления: (3.3, 2.2)',
            ],
        },
    ],
)
async def test_middle_destinations(test_case):
    destinations = test_case['test_input']['destinations']
    expected_result = test_case['expected_result']
    assert FORMATTER._middle_destinations(destinations) == expected_result


@pytest.mark.parametrize(
    'updates, translations, expected',
    [
        ([], [], []),
        (
            _CHAT_UPDATES,
            [],
            [
                {
                    'author': 'driver',
                    'created_date': '01.01.2020 03:00:00+0300',
                    'text': 'text 1',
                },
                {
                    'author': 'driver',
                    'created_date': '01.01.2020 03:00:01+0300',
                    'text': 'text 2',
                },
            ],
        ),
        (
            _CHAT_UPDATES,
            _CHAT_TRANSLATIONS,
            [
                {
                    'author': 'driver',
                    'created_date': '01.01.2020 03:00:00+0300',
                    'text': 'text 1',
                    'translation': 'translation 1',
                },
                {
                    'author': 'driver',
                    'created_date': '01.01.2020 03:00:01+0300',
                    'text': 'text 2',
                    'translation': 'translation 2',
                },
            ],
        ),
    ],
)
async def test_chat(updates, translations, expected):
    res = FORMATTER._chat(updates, translations, 'Europe/Moscow')
    assert res == expected
