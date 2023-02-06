import datetime

from aiohttp import web
import bson
import pytest

from taxi_receipt_fetching.stq import task
from test_taxi_receipt_fetching import response_data


# pylint: disable=too-many-locals,too-many-arguments
@pytest.mark.parametrize(
    'api_response',
    [
        response_data.MOLDOVA_CREATED_RESPONSE,
        response_data.MOLDOVA_CREATED_RESPONSE,
        response_data.MOLDOVA_RIDE_EXISTED_RESPONSE,
    ],
)
@pytest.mark.config(
    MOLDOVA_RIDE_REGISTRATION_ENABLED=True,
    MOLDOVA_SERVICE_DESCRIPTION_BY_TARIFF={'econom': 'TAXI ECONOM'},
    RECEIPT_REGISTRATION_ENABLED={'__default__': True},
)
async def test_fetch_ok(
        stq3_context,
        fetch_receipt_task_info,
        http_client_make_request_mock,
        load_json,
        archive_mock,
        order_proc_retrieve_mock,
        br_person_mock,
        simple_secdist,
        mongo,
        user_api_mock,
        monkeypatch,
        personal_api_mock,
        api_response,
        driver_profiles_mock,
        mockserver,
):
    order_id = '1ae95db96f726dd69ed343706d97589c'
    query = stq3_context.postgres_queries['read_receipt.sql']
    args = ([order_id],)
    postgres = stq3_context.postgresql.receipt_fetching[0]
    rows = await postgres.primary_fetch(query, *args)
    assert not rows

    make_request_mock = http_client_make_request_mock(api_response)
    archive_proc_mock = order_proc_retrieve_mock(load_json('order_proc.json'))
    archive_order_mock = archive_mock(
        load_json('orders.json'), 'get_order_by_id',
    )
    br_mock = br_person_mock(load_json('billing_replication.json'))
    driver_profile = {
        'data': {'full_name': {'first_name': 'Ivan', 'last_name': 'Ivanov'}},
    }
    profiles_mock = driver_profiles_mock(driver_profile)
    ua_data = {
        'id': 'b88fe5eedd4247da8794d70a',
        'phone': '+1234',
        'personal_phone_id': '123321',
        'type': '1',
        'stat': '1',
        'is_loyal': True,
        'is_yandex_staff': True,
        'is_taxi_staff': True,
    }
    ua_mock = user_api_mock(ua_data)
    monkeypatch.setattr(
        stq3_context.config, 'USER_API_USE_USER_PHONES_RETRIEVAL_PY3', True,
    )

    personal_mock = personal_api_mock({'id': '123321', 'value': '+71234'})

    now = datetime.datetime.utcnow()
    await mongo.tariffs.insert_one(
        {
            '_id': bson.ObjectId(),
            'home_zone': 'moscow',
            'date_from': now - datetime.timedelta(days=2),
            'date_to': now - datetime.timedelta(days=1),
            'categories': [
                {'id': 'cat_id1_1'},
                {
                    'id': 'surge--4043dc2b9dde4c5b96297244bcf1453d--mi',
                    'minimal': 1,
                },
            ],
        },
    )
    now = datetime.datetime.utcnow()
    await mongo.parks.insert_one(
        {
            '_id': '643753730232',
            'city': 'keke',
            'account': {
                'details': {
                    'inn': '123',
                    'legal_address': 'keke',
                    'long_name': 'azaza',
                },
            },
            'billing_client_ids': [
                (now - datetime.timedelta(seconds=10), None, '1'),
            ],
        },
    )

    @mockserver.json_handler('/pricing-admin/v1/receipt/md')
    def _get_pricing_receipt_data(request):
        return {
            'error_flag': False,
            'receipt': {
                'ride_start_cost': '100.00',
                'ride_waiting_time': 1,
                'ride_waiting_cost': '50.00',
                'ride_transit_waiting_time': 5,
                'ride_transit_waiting_cost': '20',
                'ride_destination_waiting_time': 2,
                'ride_destination_waiting_cost': '30.00',
                'ride_total_time_sec': 1234,
                'ride_total_distance_km': '100.50',
                'ride_cost': '1234.56',
                'ride_zones': [
                    {
                        'zone_name': 'msk',
                        'ride_distance_km': '50.00',
                        'ride_distance_cost': '50.00',
                        'ride_time_sec': 123,
                        'ride_time_cost': '100.00',
                        'tariff_distance_price': '5.00',
                        'tariff_time_price': '1.0',
                    },
                ],
                'ride_discount_amount': '10.0',
                'tariff_waiting_price': '1.0',
                'tariff_transit_waiting_price': '2.0',
                'tariff_destination_waiting_price': '3.0',
            },
        }

    await task.fetch_receipt(stq3_context, fetch_receipt_task_info, order_id)

    assert len(make_request_mock.calls) == 1
    assert len(archive_proc_mock.calls) == 1
    assert len(archive_order_mock.calls) == 1
    assert len(br_mock.calls) == 1
    assert len(personal_mock.calls) == 1
    assert len(profiles_mock.calls) == 1
    assert len(ua_mock.calls) == 1
    assert _get_pricing_receipt_data.times_called == 1

    rows = await postgres.primary_fetch(query, *args)
    assert len(rows) == 1
    assert rows[0]['order_id'] == order_id
    assert (
        rows[0]['receipt_url']
        == f'https://api.etaxi.md/api/y/ride_mobile/{order_id}'
    )


@pytest.mark.parametrize(
    'pricing_data_response',
    [
        (404, {'code': 'ORDER_NOT_FOUND', 'message': ''}),
        (422, {'code': 'OLD_PRICING_ORDER', 'message': ''}),
        (
            200,
            {
                'error_flag': True,
                'receipt': {
                    'ride_cost': '0',
                    'ride_total_distance_km': '0',
                    'ride_total_time_sec': 0,
                    'ride_zones': [],
                },
            },
        ),
    ],
)
@pytest.mark.config(
    MOLDOVA_RIDE_REGISTRATION_ENABLED=True,
    MOLDOVA_SERVICE_DESCRIPTION_BY_TARIFF={'econom': 'TAXI ECONOM'},
    RECEIPT_REGISTRATION_ENABLED={'__default__': True},
)
async def test_reschedule_task_on_pricing_data_errors(
        stq3_context,
        fetch_receipt_task_info,
        load_json,
        archive_mock,
        order_proc_retrieve_mock,
        simple_secdist,
        mockserver,
        pricing_data_response,
):
    order_id = '1ae95db96f726dd69ed343706d97589c'
    query = stq3_context.postgres_queries['read_receipt.sql']
    args = ([order_id],)
    postgres = stq3_context.postgresql.receipt_fetching[0]
    rows = await postgres.primary_fetch(query, *args)
    assert not rows

    archive_proc_mock = order_proc_retrieve_mock(load_json('order_proc.json'))
    archive_order_mock = archive_mock(
        load_json('orders.json'), 'get_order_by_id',
    )

    @mockserver.handler('/pricing-admin/v1/receipt/md')
    def _get_pricing_receipt_data(request):
        return web.json_response(
            status=pricing_data_response[0], data=pricing_data_response[1],
        )

    task_rescheduled = False

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _reschedule(request):
        assert request.json['queue_name'] == 'fetch_receipt'
        nonlocal task_rescheduled
        task_rescheduled = True

    await task.fetch_receipt(stq3_context, fetch_receipt_task_info, order_id)

    assert len(archive_proc_mock.calls) == 1
    assert len(archive_order_mock.calls) == 1
    assert _get_pricing_receipt_data.times_called == 1
    assert task_rescheduled

    rows = await postgres.primary_fetch(query, *args)
    assert not rows
