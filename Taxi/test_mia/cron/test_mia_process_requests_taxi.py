# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines
# flake8: noqa

import pytest

from mia.generated.cron import run_cron
from test_mia.cron import timezone_dummy
from test_mia.cron import user_phone_dummy
from test_mia.cron import yt_dummy


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'query_name,expected_matches',
    [
        (
            'mia_request_query_simple',
            [
                {
                    'created_time': '04.03.2019 20:56:35+0300',
                    'from': '-',
                    'is_completed': False,
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'order_id': 'test_order_id',
                    'middle_destinations': [],
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
        ),
        (
            'mia_request_query_complex',
            [
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                        'Тестовый переулок, дом 123 | точка отправления: (60.12, 70.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_2',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
        ),
        (
            'mia_request_without_period',
            [
                {
                    'created_time': '22.02.2019 15:44:57+0300',
                    'from': '-',
                    'is_completed': False,
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'middle_destinations': [],
                    'order_id': 'test_order_id_3',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'created_time': '22.03.2019 15:44:57+0300',
                    'from': '-',
                    'is_completed': False,
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'middle_destinations': [],
                    'order_id': 'test_order_id_3',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
        ),
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi(
        patch, load_json, taxi_mia_web, query_name, expected_matches,
):
    yt_tables = load_json('yt_tables.json')
    request = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    response = await taxi_mia_web.post('/v1/taxi/query', request)
    content = await response.json()

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/taxi/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expected_matches


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=True,
    MIA_COUNTRIES_BINDINGS={
        'RU': ['Россия', 'Российская Федерация', 'Russia'],
        'BL': ['Беларусь', 'Belarus'],
    },
)
@pytest.mark.parametrize(
    'query_name,expected_matches,solomon_metrics',
    [
        (
            'mia_request_query_in_russia',
            [
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_2',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_with_different_countries_in_destinations',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_with_country_in_source',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_with_unknown_country',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_without_country',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
            [
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Russia',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Russia',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Российская Федерация',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'unknown_country',
                    },
                    'kind': 'IGAUGE',
                    'value': 1,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
            ],
        ),
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi_with_country_filter(
        patch,
        load_json,
        taxi_mia_web,
        query_name,
        expected_matches,
        solomon_metrics,
):
    yt_tables = load_json('yt_tables_with_countries.json')
    request = load_json(query_name + '.json')

    @patch('taxi.clients.solomon.SolomonClient._request')
    async def solomon_mock(*args, data=None, **kwargs):
        pass

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    response = await taxi_mia_web.post('/v1/taxi/query', request)
    content = await response.json()

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/taxi/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expected_matches

    solomon_calls = solomon_mock.calls
    assert len(solomon_calls) == 2
    data = solomon_calls[0]['data']
    excepted_ts = 1562242800
    assert data['ts'] == excepted_ts
    assert data['sensors'] == solomon_metrics


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_COUNTRIES_BINDINGS={
        'RU': ['Россия', 'Российская Федерация', 'Russia'],
        'BL': ['Беларусь', 'Belarus'],
    },
)
@pytest.mark.parametrize(
    'query_name,expected_matches,solomon_metrics',
    [
        (
            'mia_request_query_in_russia_countries',
            [
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_2',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_with_different_countries_in_destinations',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'order_id': 'test_order_id_with_country_in_source',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'order_id': 'test_order_id_with_other_country',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_with_unknown_country',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
                {
                    'arrival_point': [-100, 100],
                    'canceled_time': '07.04.2019 21:06:35+0300',
                    'cancellation_reason': 'reason 1, reason 2',
                    'car_number': 'СА100B',
                    'cost': '100$',
                    'created_time': '07.04.2019 20:56:35+0300',
                    'driver_id': 'performer_driver_id',
                    'driver_license': 'test_driver_license',
                    'driver_name': 'Василий Михайлович Тестовый',
                    'driver_phone': '+79990003412',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'finished_time': '09.03.1973 07:45:00+0300',
                    'from': (
                        'Тестовая улица, дом 10 '
                        '| точка отправления: (-10, 10)'
                    ),
                    'middle_destinations': [
                        'Какая-то промежуточная остановка | точка отправления: (90.12, 89.52)',
                    ],
                    'is_completed': True,
                    'order_id': 'test_order_id_without_country',
                    'order_id_for_partners': 'some_performer_taxi_alias_id',
                    'passenger_phone': '+79990001234',
                    'user_phone': '+79990001234',
                    'payment_method': 'наличные',
                    'request_due': '08.04.2019 02:26:35+0300',
                    'to': (
                        'Проспект Летаргии, дом 9910 '
                        '| точка отправления: (-100, 100)'
                    ),
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
            [
                {  # 0
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Russia',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Russia',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {  # 5
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Российская Федерация',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'application': 'mia',
                        'country': 'Belarus',
                        'sensor': 'mia-countries',
                    },
                    'ts': 1562242800,
                    'value': 0,
                },
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'application': 'mia',
                        'country': 'Belarus',
                        'sensor': 'mia-countries',
                    },
                    'ts': 1562242800,
                    'value': 0,
                },
                {  # 10
                    'kind': 'IGAUGE',
                    'labels': {
                        'application': 'mia',
                        'country': 'Беларусь',
                        'sensor': 'mia-countries',
                    },
                    'ts': 1562242800,
                    'value': 0,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'unknown_country',
                    },
                    'kind': 'IGAUGE',
                    'value': 1,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Belarus',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
                {  # 15
                    'labels': {
                        'application': 'mia',
                        'sensor': 'mia-countries',
                        'country': 'Беларусь',
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                    'ts': 1562242800,
                },
            ],
        ),
    ],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi_with_countries_filter(
        patch,
        load_json,
        taxi_mia_web,
        query_name,
        expected_matches,
        solomon_metrics,
):
    yt_tables = load_json('yt_tables_with_countries.json')
    request = load_json(query_name + '.json')

    @patch('taxi.clients.solomon.SolomonClient._request')
    async def solomon_mock(*args, data=None, **kwargs):
        pass

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    response = await taxi_mia_web.post('/v1/taxi/query', request)
    content = await response.json()

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/taxi/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expected_matches

    solomon_calls = solomon_mock.calls
    assert len(solomon_calls) == 2
    data = solomon_calls[0]['data']
    excepted_ts = 1562242800
    assert data['ts'] == excepted_ts
    assert data['sensors'] == solomon_metrics


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=True,
    MIA_COUNTRIES_BINDINGS={
        'RU': ['Россия', 'Российская Федерация', 'Russia'],
        'BL': ['Беларусь', 'Belarus'],
    },
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_requests_taxi_with_unknown_country(
        patch, load_json, taxi_mia_web,
):
    request = {
        'check_all_candidates': False,
        'exact': {'order_id': 'test_order_id'},
        'country': 'UNKNOWN',
    }

    response = await taxi_mia_web.post('/v1/taxi/query', request)
    assert response.status == 400
    assert await response.json() == {'message': 'Unknown country!'}


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=1,
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_priority_order_taxi(patch, load_json, taxi_mia_web, test):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    order_num_to_priority = {0: '4', 1: '1', 2: '3', 3: '2'}
    order_num_to_id = {}
    order_num_to_status = {}

    for order_num, priority in order_num_to_priority.items():
        response = await taxi_mia_web.post(
            f'/v1/taxi/query/?priority={priority}', request_body,
        )
        content = await response.json()
        order_num_to_id[order_num] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=1,
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_priority_equal_order_taxi(
        patch, load_json, taxi_mia_web, test,
):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    order_num_to_priority = {0: '3', 1: '3', 2: '4', 3: '3'}
    order_num_to_id = {}
    order_num_to_status = {}

    for order_num, priority in order_num_to_priority.items():
        response = await taxi_mia_web.post(
            f'/v1/taxi/query/?priority={priority}', request_body,
        )
        content = await response.json()
        order_num_to_id[order_num] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'pending'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=1,
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-07-04T12:20:00.0')
async def test_mia_process_in_order_taxi(patch, load_json, taxi_mia_web, test):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    order_num_to_id = {}
    order_num_to_status = {}

    for i in range(4):
        response = await taxi_mia_web.post(f'/v1/taxi/query/', request_body)
        content = await response.json()
        order_num_to_id[i] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=4,
    MIA_SEARCH_OPERATION_RETRY={'retry_count': 3, 'retry_sleep_delay': 0},
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-06-06T12:20:00.0')
async def test_mia_run_fail(patch, load_json, taxi_mia_web, test):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    order_num_to_id = {}
    order_num_to_status = {}
    fail_request_ids = set()
    for i in range(7):
        response = await taxi_mia_web.post(f'/v1/taxi/query/', request_body)
        content = await response.json()
        if i in {2, 6}:
            fail_request_ids.add(int(content['id']))
        order_num_to_id[i] = content['id']

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(
            yt_tables, fail_requests=fail_request_ids,
        )

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'
    assert order_num_to_status[4] == 'pending'
    assert order_num_to_status[5] == 'pending'
    assert order_num_to_status[6] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'failed'
    assert order_num_to_status[3] == 'pending'
    assert order_num_to_status[4] == 'pending'
    assert order_num_to_status[5] == 'pending'
    assert order_num_to_status[6] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'failed'
    assert order_num_to_status[3] == 'succeeded'
    assert order_num_to_status[4] == 'succeeded'
    assert order_num_to_status[5] == 'pending'
    assert order_num_to_status[6] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'failed'
    assert order_num_to_status[3] == 'succeeded'
    assert order_num_to_status[4] == 'succeeded'
    assert order_num_to_status[5] == 'succeeded'
    assert order_num_to_status[6] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'failed'
    assert order_num_to_status[3] == 'succeeded'
    assert order_num_to_status[4] == 'succeeded'
    assert order_num_to_status[5] == 'succeeded'
    assert order_num_to_status[6] == 'failed'


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=2,
    MIA_SEARCH_OPERATION_RETRY={'retry_count': 2, 'retry_sleep_delay': 0},
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-06-06T12:20:00.0')
async def test_mia_await_fail(patch, load_json, taxi_mia_web, test):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    order_num_to_id = {}
    order_num_to_status = {}
    for i in range(3):
        response = await taxi_mia_web.post(f'/v1/taxi/query/', request_body)
        content = await response.json()
        order_num_to_id[i] = content['id']

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables, ruin_await_count=3)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.pgsql('mia', files=['pg_mia_process_finalizing_taxi.sql'])
@pytest.mark.parametrize(
    'test',
    [
        {
            'expected': [
                {
                    'created_time': '04.03.2019 20:56:35+0300',
                    'from': '-',
                    'is_completed': False,
                    'middle_destinations': [],
                    'order_id': 'test_order_id',
                    'aggregator': '-',
                    'aggregator_phone': '-',
                    'park_name': '-',
                    'park_phone': '-',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                },
            ],
        },
    ],
)
@pytest.mark.now('2019-03-05T12:20:00.0')
async def test_mia_process_finalizing_taxi(
        patch, load_json, taxi_mia_web, test,
):
    expected = test['expected']
    yt_tables = load_json('yt_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/taxi/query/123', {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expected


@pytest.mark.config(
    MIA_QUERIES_BATCH_SIZE=2,
    MIA_SEARCH_OPERATION_RETRY={'retry_count': 1, 'retry_sleep_delay': 0},
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_request_query_simple'}}],
)
@pytest.mark.now('2019-06-06T12:20:00.0')
async def test_mia_await_fail_request(patch, load_json, taxi_mia_web, test):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    order_num_to_id = {}
    order_num_to_status = {}
    for i in range(3):
        response = await taxi_mia_web.post(f'/v1/taxi/query/', request_body)
        content = await response.json()
        order_num_to_id[i] = content['id']

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables, ruin_await_count=2)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/taxi/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'failed'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'failed'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
