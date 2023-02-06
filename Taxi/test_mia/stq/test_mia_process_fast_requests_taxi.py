# pylint: disable=redefined-outer-name
import pytest

from mia.crontasks import pg_wrapper
from mia.stq import mia_process_fast_request
from test_mia.cron import scrooge_wrapper_dummy
from test_mia.cron import timezone_dummy
from test_mia.cron import user_phone_dummy
from test_mia.cron import yt_dummy


@pytest.fixture()
def mock_stq_dependencies(patch, load_json):
    yt_tables = load_json('yt_tables.json')
    scrooge_tables = load_json('scrooge_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {
                '+79990001234': ['id_of_79990001234'],
                '+79990001235': ['id_of_79990001235'],
                '+79990001236': ['id_of_79990001236'],
                '+79990001237': ['id_of_79990001237'],
                '+79990001238': ['id_of_79990001238'],
            },
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    @patch('mia.crontasks.dependencies._create_scrooge_wrapper')
    def _create_scrooge_wrapper(_):
        return scrooge_wrapper_dummy.ScroogeWrapperDummy(scrooge_tables)


async def _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expectred_result,
):
    response = await taxi_mia_web.post('/v1/taxi/query', request)
    content = await response.json()
    await mia_process_fast_request.task(
        stq3_context,
        mia_query_id=int(content['id']),
        service_name=pg_wrapper.ServiceName.TAXI.name,
    )
    response = await taxi_mia_web.get('/v1/taxi/query/' + content['id'], {})
    content = await response.json()
    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expectred_result


@pytest.mark.config(MIA_FAST_QUERIES_ENABLED=True)
@pytest.mark.parametrize(
    'case',
    [
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
            },
        },
        {
            'request': {
                'exact': {'user_phone': '+79990001234'},
                'check_all_candidates': False,
            },
        },
        {
            'request': {
                'exact': {'driver_license': 'test_driver_license'},
                'check_all_candidates': False,
                'period': {
                    'created': {
                        'from': '2019-03-28T12:00:00.0',
                        'to': '2019-04-14T12:00:00.0',
                    },
                },
            },
        },
        {
            'request': {
                'exact': {'driver_phone': '+79990003412'},
                'check_all_candidates': False,
                'period': {
                    'created': {
                        'from': '2019-03-28T12:00:00.0',
                        'to': '2019-04-14T12:00:00.0',
                    },
                },
            },
        },
        {
            'request': {
                'exact': {'license_plates': 'СА100B'},
                'check_all_candidates': False,
                'period': {
                    'created': {
                        'from': '2019-03-28T12:00:00.0',
                        'to': '2019-04-14T12:00:00.0',
                    },
                },
            },
        },
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi(
        taxi_mia_web, case, stq, stq3_context, mock_stq_dependencies,
):
    request = case['request']
    expected = [
        {
            'created_time': '07.04.2019 20:56:35+0300',
            'from': 'Тестовая улица, дом 10 | точка отправления: (-10, 10)',
            'is_completed': True,
            'order_id': 'test_order_id_2',
            'arrival_point': [-100, 100],
            'canceled_time': '07.04.2019 21:06:35+0300',
            'cancellation_reason': 'reason 1, reason 2',
            'car_number': 'СА100B',
            'cost': '100$',
            'middle_destinations': [
                (
                    'Какая-то промежуточная остановка | точка отправления: '
                    '(90.12, 89.52)'
                ),
            ],
            'driver_id': 'performer_driver_id',
            'aggregator': '-',
            'aggregator_phone': '-',
            'park_name': '-',
            'park_phone': '-',
            'driver_license': 'test_driver_license',
            'driver_name': 'Василий Михайлович Тестовый',
            'driver_phone': '+79990003412',
            'finished_time': '09.03.1973 07:45:00+0300',
            'order_id_for_partners': 'some_performer_taxi_alias_id',
            'passenger_phone': '+79990001234',
            'user_phone': '+79990001234',
            'payment_method': 'наличные',
            'request_due': '08.04.2019 02:26:35+0300',
            'to': (
                'Проспект Летаргии, дом 9910 | точка отправления: (-100, 100)'
            ),
            'masked_pan': '-',
            'rrn': '-',
            'approval_code': '-',
            'payment_time': '-',
        },
    ]

    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expected,
    )


@pytest.mark.config(MIA_FAST_QUERIES_ENABLED=True)
@pytest.mark.parametrize(
    'case',
    [
        {
            'request': {
                'exact': {'taximeter_order_number': 1},
                'check_all_candidates': False,
                'period': {
                    'request_due': {
                        'from': '2019-04-06T12:00:00.0',
                        'to': '2019-04-08T12:00:00.0',
                    },
                },
            },
        },
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_taximeter_order_number_search(
        taxi_mia_web, case, stq, stq3_context, mock_stq_dependencies,
):
    request = case['request']
    expected = [
        {
            'created_time': '07.04.2019 20:56:35+0300',
            'from': 'Тестовая улица, дом 10 | точка отправления: (-10, 10)',
            'is_completed': True,
            'taximeter_order_number': 1,
            'order_id': 'test_order_id_2',
            'arrival_point': [-100, 100],
            'canceled_time': '07.04.2019 21:06:35+0300',
            'cancellation_reason': 'reason 1, reason 2',
            'car_number': 'СА100B',
            'cost': '100$',
            'aggregator': '-',
            'aggregator_phone': '-',
            'park_name': '-',
            'park_phone': '-',
            'middle_destinations': [
                (
                    'Какая-то промежуточная остановка | точка отправления: '
                    '(90.12, 89.52)'
                ),
            ],
            'driver_id': 'performer_driver_id',
            'driver_license': 'test_driver_license',
            'driver_name': 'Василий Михайлович Тестовый',
            'driver_phone': '+79990003412',
            'finished_time': '09.03.1973 07:45:00+0300',
            'order_id_for_partners': 'some_performer_taxi_alias_id',
            'passenger_phone': '+79990001234',
            'user_phone': '+79990001234',
            'payment_method': 'наличные',
            'request_due': '08.04.2019 02:26:35+0300',
            'to': (
                'Проспект Летаргии, дом 9910 | точка отправления: (-100, 100)'
            ),
            'masked_pan': '-',
            'rrn': '-',
            'approval_code': '-',
            'payment_time': '-',
        },
    ]

    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expected,
    )


@pytest.mark.config(
    MIA_FAST_QUERIES_ENABLED=True,
    MIA_FILTER_BY_COUNTRIES_ENABLED=True,
    MIA_COUNTRIES_BINDINGS={
        'RU': ['Россия', 'Российская Федерация', 'Russia'],
        'BL': ['Беларусь', 'Belarus'],
        'UK': ['Украина', 'Ukraine'],
    },
)
@pytest.mark.parametrize(
    'case',
    [
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'country': 'RU',
            },
        },
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'country': 'BL',
            },
        },
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'country': 'UK',
            },
            'expected': [],
        },
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi_with_country(
        taxi_mia_web, case, stq, stq3_context, mock_stq_dependencies,
):
    request = case['request']
    # pylint: disable=line-too-long
    expected = case.get(
        'expected',
        [
            {
                'created_time': '07.04.2019 20:56:35+0300',
                'from': (
                    'Тестовая улица, дом 10 | точка отправления: (-10, 10)'
                ),
                'is_completed': True,
                'order_id': 'test_order_id_2',
                'arrival_point': [-100, 100],
                'canceled_time': '07.04.2019 21:06:35+0300',
                'cancellation_reason': 'reason 1, reason 2',
                'car_number': 'СА100B',
                'cost': '100$',
                'middle_destinations': [
                    (
                        'Какая-то промежуточная остановка | точка'
                        ' отправления: (90.12, 89.52)'
                    ),
                ],
                'driver_id': 'performer_driver_id',
                'driver_license': 'test_driver_license',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'driver_name': 'Василий Михайлович Тестовый',
                'driver_phone': '+79990003412',
                'finished_time': '09.03.1973 07:45:00+0300',
                'order_id_for_partners': 'some_performer_taxi_alias_id',
                'passenger_phone': '+79990001234',
                'user_phone': '+79990001234',
                'payment_method': 'наличные',
                'request_due': '08.04.2019 02:26:35+0300',
                'to': (
                    'Проспект Летаргии, дом 9910 | '
                    'точка отправления: (-100, 100)'
                ),
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
            },
        ],
    )

    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expected,
    )


@pytest.mark.config(
    MIA_FAST_QUERIES_ENABLED=True,
    MIA_FILTER_BY_COUNTRIES_ENABLED=True,
    MIA_COUNTRIES_BINDINGS={
        'RU': ['Россия', 'Российская Федерация', 'Russia'],
        'BL': ['Беларусь', 'Belarus'],
        'UK': ['Украина', 'Ukraine'],
    },
)
@pytest.mark.parametrize(
    'case',
    [
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'countries': ['RU'],
            },
        },
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'countries': ['BL'],
            },
        },
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'countries': ['UK'],
            },
            'expected': [],
        },
        {
            'request': {
                'exact': {'order_id': 'test_order_id_2'},
                'check_all_candidates': False,
                'countries': ['RU', 'BL'],
            },
        },
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi_with_countries(
        taxi_mia_web, case, stq, stq3_context, mock_stq_dependencies,
):
    request = case['request']
    # pylint: disable=line-too-long
    expected = case.get(
        'expected',
        [
            {
                'created_time': '07.04.2019 20:56:35+0300',
                'from': (
                    'Тестовая улица, дом 10 | точка отправления: (-10, 10)'
                ),
                'is_completed': True,
                'order_id': 'test_order_id_2',
                'arrival_point': [-100, 100],
                'canceled_time': '07.04.2019 21:06:35+0300',
                'cancellation_reason': 'reason 1, reason 2',
                'car_number': 'СА100B',
                'cost': '100$',
                'aggregator': '-',
                'aggregator_phone': '-',
                'park_name': '-',
                'park_phone': '-',
                'middle_destinations': [
                    (
                        'Какая-то промежуточная остановка | точка'
                        ' отправления: (90.12, 89.52)'
                    ),
                ],
                'driver_id': 'performer_driver_id',
                'driver_license': 'test_driver_license',
                'driver_name': 'Василий Михайлович Тестовый',
                'driver_phone': '+79990003412',
                'finished_time': '09.03.1973 07:45:00+0300',
                'order_id_for_partners': 'some_performer_taxi_alias_id',
                'passenger_phone': '+79990001234',
                'user_phone': '+79990001234',
                'payment_method': 'наличные',
                'request_due': '08.04.2019 02:26:35+0300',
                'to': (
                    'Проспект Летаргии, дом 9910 | '
                    'точка отправления: (-100, 100)'
                ),
                'masked_pan': '-',
                'payment_time': '-',
                'rrn': '-',
                'approval_code': '-',
            },
        ],
    )

    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expected,
    )


@pytest.mark.config(
    MIA_SCROOGE_TAXI_SERVICE_IDS=[124], MIA_FAST_QUERIES_ENABLED=True,
)
@pytest.mark.now('2019-07-04T12:20:00.0')
@pytest.mark.parametrize(
    'case',
    [
        {
            'test_input': {
                'request': {
                    'check_all_candidates': False,
                    'exact': {
                        'masked_pan': '123456****1234',
                        'rrn': 'test_rrn_2',
                        'approval_code': 'test_approval_code_2',
                        'order_cost': 234,
                    },
                    'period': {
                        'payment': {
                            'from': '2019-04-05T11:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected_result': [
                {
                    'created_time': '07.04.2019 20:56:35+0300',
                    'from': (
                        'Тестовая улица, дом 10 | точка отправления: (-10, 10)'
                    ),
                    'is_completed': True,
                    'order_id': 'test_order_id_2',
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '234',
                    'middle_destinations': [
                        (
                            'Какая-то промежуточная остановка | точка '
                            'отправления: (90.12, 89.52)'
                        ),
                    ],
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 | '
                        'точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '123456****1234',
                    'rrn': 'test_rrn_2',
                    'approval_code': 'test_approval_code_2',
                    'payment_time': '07.04.2019 21:07:00+0300',
                },
            ],
        },
        {
            'test_input': {
                'request': {
                    'check_all_candidates': False,
                    'exact': {
                        'masked_pan': '123456****1234',
                        'order_cost': 234,
                        'order_id': 'test_order_id_2',
                        'user_phone': '+79990001234',
                        'driver_license': 'test_driver_license',
                        'driver_phone': '+79990003412',
                        'license_plates': 'СА100B',
                    },
                    'period': {
                        'payment': {
                            'from': '2019-04-05T11:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected_result': [
                {
                    'created_time': '07.04.2019 20:56:35+0300',
                    'from': (
                        'Тестовая улица, дом 10 | точка отправления: (-10, 10)'
                    ),
                    'is_completed': True,
                    'order_id': 'test_order_id_2',
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '234',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'middle_destinations': [
                        (
                            'Какая-то промежуточная остановка | точка '
                            'отправления: (90.12, 89.52)'
                        ),
                    ],
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 | '
                        'точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '123456****1234',
                    'payment_time': '07.04.2019 21:07:00+0300',
                    'approval_code': 'test_approval_code_2',
                    'rrn': 'test_rrn_2',
                },
            ],
        },
    ],
)
async def test_mia_process_fast_requests_taxi_new(
        taxi_mia_web, stq, stq3_context, case, mock_stq_dependencies,
):
    request = case['test_input']['request']
    expectred_result = case['expected_result']
    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expectred_result,
    )


@pytest.mark.config(MIA_FAST_QUERIES_ENABLED=True)
@pytest.mark.now('2019-07-04T12:20:00.0')
@pytest.mark.parametrize(
    'user_phone',
    ['+79990001235', '+79990001236', '+79990001237', '+79990001238'],
)
async def test_mia_process_fast_requests_taxi_user_phones(
        taxi_mia_web, stq, stq3_context, user_phone, mock_stq_dependencies,
):
    request = {
        'exact': {'user_phone': user_phone},
        'check_all_candidates': False,
    }
    expected = [
        {
            'created_time': '07.04.2019 20:56:35+0300',
            'from': 'Тестовая улица, дом 10 | точка отправления: (-10, 10)',
            'is_completed': True,
            'order_id': 'test_order_id_3',
            'arrival_point': [-100, 100],
            'canceled_time': '07.04.2019 21:06:35+0300',
            'cancellation_reason': 'reason 1, reason 2',
            'car_number': 'СА100B',
            'cost': '100$',
            'middle_destinations': [
                (
                    'Какая-то промежуточная остановка | точка '
                    'отправления: (90.12, 89.52)'
                ),
            ],
            'driver_id': 'performer_driver_id',
            'driver_license': 'test_driver_license',
            'driver_name': 'Василий Михайлович Тестовый',
            'driver_phone': '+79990003412',
            'aggregator': '-',
            'aggregator_phone': '-',
            'park_name': '-',
            'park_phone': '-',
            'finished_time': '09.03.1973 07:45:00+0300',
            'order_id_for_partners': 'some_performer_taxi_alias_id',
            'passenger_phone': '+79990001235',
            'user_phone': '+79990001238',
            'payment_method': 'наличные',
            'request_due': '08.04.2019 02:26:35+0300',
            'to': (
                'Проспект Летаргии, дом 9910 | '
                'точка отправления: (-100, 100)'
            ),
            'masked_pan': '-',
            'rrn': '-',
            'approval_code': '-',
            'payment_time': '-',
            'source_contact_phone': '+79990001237',
            'destination_contact_phones': ['+79990001236'],
        },
    ]
    await _send_request_and_check_result(
        stq3_context, taxi_mia_web, request, expected,
    )
