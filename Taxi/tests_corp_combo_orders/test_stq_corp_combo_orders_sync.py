import datetime

import psycopg2
import pytest

DUE_DATE = datetime.datetime(
    2021, 12, 8, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
)
EVENT_DATE = datetime.datetime(
    2021, 12, 9, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
)

ORDER_SQL_QUERY = (
    'SELECT destination, interim_destinations, status, '
    'taxi_status, due_date, finished_date, version '
    'FROM corp_combo_orders.orders WHERE id = %s ORDER BY id;'
)

STQ_REQUEST_KWARGS = {
    'order_id': 'test_order_id',
    'version': 10,
    'taxi_status': 'driving',
    'status': 'assigned',
    'due_date': DUE_DATE.isoformat(),
    'event_date': EVENT_DATE.isoformat(),
    'destinations': [
        {
            'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            'country': 'Россия',
            'geopoint': [1, 2],
            'short_text': 'Тверская улица, 18к1',
            'locality': 'Москва',
            'thoroughfare': 'Тверская улица',
            'premisenumber': '18к1',
            'type': 'address',
            'object_type': 'другое',
            'description': 'Москва, Россия',
            'uris': ['ymapsbm1://...'],
        },
    ],
}

BASE_DB_DESTINATION = {
    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
    'geopoint': [1, 2],
}

NEW_DESTINATIONS = [
    {
        'fullname': 'Россия, Москва, Тверская улица, 18к1',
        'country': 'Россия',
        'geopoint': [37.6039000014267, 55.7657515910581],
        'short_text': 'Тверская улица, 18к1',
        'locality': 'Москва',
        'thoroughfare': 'Тверская улица',
        'premisenumber': '18к1',
        'type': 'address',
        'object_type': 'другое',
        'description': 'Москва, Россия',
        'uris': ['ymapsbm1://...'],
    },
    {
        'fullname': 'Россия, Москва, улица Кузнецкий Мост, 22с4',
        'country': 'Россия',
        'geopoint': [37.62451633719725, 55.76151237249842],
        'short_text': 'улица Кузнецкий Мост, 22с4',
        'locality': 'Москва',
        'thoroughfare': 'улица Кузнецкий Мост',
        'premisenumber': '22с4',
        'type': 'address',
        'object_type': 'другое',
        'description': 'Москва, Россия',
        'uris': ['ymapsbm1://...'],
    },
]

INT_API_ORDER_INFO = {
    'driver': {'name': 'Рябов Якуб Аверьянович', 'phone': '+70003661581'},
    'orderid': '7b758b742a0fc42abdcfaa229e784132',
    'route_sharing_url': '...',
    'status': 'complete',
    'time_left': '5 мин',
    'time_left_raw': 310.0,
    'vehicle': {
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Renault Clio',
        'plates': 'С179РЕ77',
        'short_car_number': '179',
    },
}

EXPECTED_ASSIGNED_SMS_REQUEST = {
    'text': 'Вам оплатили такси: ...\nПриедет через 5 мин С179РЕ77',
    'intent': 'taxi_order_corpweb_on_assigned_taxi',
}
EXPECTED_WAITING_SMS_REQUEST = {
    'text': (
        'Водитель на месте\nФиолетовый Renault Clio С179РЕ77\n+70003661581'
    ),
    'intent': 'taxi_order_corpweb_on_waiting_taxi',
}


@pytest.mark.pgsql('corp_combo_orders', files=['insert_orders.sql'])
async def test_outdated_event(stq_runner, mockserver, pgsql):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _search_order(request):
        return mockserver.make_response(
            json={'orders': [INT_API_ORDER_INFO]}, status=200,
        )

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute(ORDER_SQL_QUERY, ('test_order_id',))
    orders_before_stq = list(cursor)

    await stq_runner.corp_combo_orders_sync.call(
        task_id='sample_task', kwargs={**STQ_REQUEST_KWARGS, **{'version': 9}},
    )

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute(ORDER_SQL_QUERY, ('test_order_id',))
    assert list(cursor) == orders_before_stq


@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'gbr': {'default_language': 'en'},
        'rus': {'default_language': 'ru'},
        'isr': {'default_language': 'en'},
        'arm': {'default_language': 'hy'},
    },
)
@pytest.mark.parametrize(
    [
        'stq_input_kwargs',
        'int_api_response',
        'expected_db_order',
        'expected_sms_calls',
        'expected_sms_call_request',
    ],
    [
        pytest.param(
            STQ_REQUEST_KWARGS,
            INT_API_ORDER_INFO,
            (
                BASE_DB_DESTINATION,
                [],
                'assigned',
                'driving',
                DUE_DATE,
                None,
                10,
            ),
            2,
            EXPECTED_ASSIGNED_SMS_REQUEST,
            id='update status to assigned',
        ),
        pytest.param(
            STQ_REQUEST_KWARGS,
            {
                **INT_API_ORDER_INFO,
                **{'route_sharing_url': None},  # type: ignore
            },
            (
                BASE_DB_DESTINATION,
                [],
                'assigned',
                'driving',
                DUE_DATE,
                None,
                10,
            ),
            0,
            None,
            id='not enough data from order search, skip sms sending',
        ),
        pytest.param(
            {**STQ_REQUEST_KWARGS, **{'taxi_status': 'waiting'}},
            INT_API_ORDER_INFO,
            (
                BASE_DB_DESTINATION,
                [],
                'assigned',
                'waiting',
                DUE_DATE,
                None,
                10,
            ),
            2,
            EXPECTED_WAITING_SMS_REQUEST,
            id='update status to waiting',
        ),
        pytest.param(
            {**STQ_REQUEST_KWARGS, **{'destinations': NEW_DESTINATIONS}},
            INT_API_ORDER_INFO,
            (
                {
                    'fullname': 'Россия, Москва, улица Кузнецкий Мост, 22с4',
                    'geopoint': [37.62451633719725, 55.76151237249842],
                },
                [
                    {
                        'fullname': 'Россия, Москва, Тверская улица, 18к1',
                        'geopoint': [37.6039000014267, 55.7657515910581],
                    },
                ],
                'assigned',
                'driving',
                DUE_DATE,
                None,
                10,
            ),
            2,
            EXPECTED_ASSIGNED_SMS_REQUEST,
            id='update statuses and interim destinations',
        ),
        pytest.param(
            {**STQ_REQUEST_KWARGS, **{'order_id': 'test_order_id_2'}},
            INT_API_ORDER_INFO,
            (
                BASE_DB_DESTINATION,
                [],
                'assigned',
                'driving',
                DUE_DATE,
                None,
                10,
            ),
            0,
            None,
            id='do not sent sms if already sent',
        ),
        pytest.param(
            {
                **STQ_REQUEST_KWARGS,
                **{'status': 'finished', 'taxi_status': 'complete'},
            },
            INT_API_ORDER_INFO,
            (
                BASE_DB_DESTINATION,
                [],
                'finished',
                'complete',
                DUE_DATE,
                EVENT_DATE,
                10,
            ),
            0,
            None,
            id='finished events, save finished_date',
        ),
        pytest.param(
            {
                **STQ_REQUEST_KWARGS,
                **{'status': 'cancelled', 'taxi_status': None},
            },
            INT_API_ORDER_INFO,
            (
                BASE_DB_DESTINATION,
                [],
                'cancelled',
                '',
                DUE_DATE,
                EVENT_DATE,
                10,
            ),
            0,
            None,
            id='cancelled event (without taxi_status)',
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'corp_combo_orders.waiting_for_passenger.text.sms': {
            'ru': 'Водитель на месте\n%(short_car_info)s\n%(performer_phone)s',
            'en': (
                'Your ride is waiting\n%(short_car_info)s\n%(performer_phone)s'
            ),
        },
        'corp_combo_orders.driving_for_passenger.text.sms': {
            'ru': (
                'Вам оплатили такси: %(share_route_url)s\n'
                'Приедет через %(short_estimate)s мин %(car_number)s'
            ),
            'en': (
                'Pre-paid ride requested for you: %(share_route_url)s\n'
                'Pickup in %(short_estimate)s min. %(car_number)s'
            ),
        },
    },
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_orders.sql'])
async def test_actual_event(
        stq_runner,
        mockserver,
        pgsql,
        stq_input_kwargs,
        int_api_response,
        expected_db_order,
        expected_sms_calls,
        expected_sms_call_request,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _search_order(request):
        return mockserver.make_response(
            json={'orders': [int_api_response]}, status=200,
        )

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _send_sms(request):
        request_body = request.json
        request_body.pop('phone_id')
        assert request_body == expected_sms_call_request
        return mockserver.make_response(
            json={'message': 'OK', 'code': '200'}, status=200,
        )

    @mockserver.json_handler('/corp-clients-uservices/v1/clients')
    def _mock_corp_clients(request):
        return {'id': 'my_id', 'country': 'rus'}

    await stq_runner.corp_combo_orders_sync.call(
        task_id='sample_task', kwargs=stq_input_kwargs,
    )

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute(ORDER_SQL_QUERY, (stq_input_kwargs['order_id'],))
    assert list(cursor) == [expected_db_order]

    assert _send_sms.times_called == expected_sms_calls
