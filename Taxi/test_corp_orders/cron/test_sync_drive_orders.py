# pylint: disable=redefined-outer-name
import copy

import pytest

from corp_orders.generated.cron import run_cron
from corp_orders.internal import base_context
from corp_orders.internal import exceptions

ADDITIONAL = {
    'finish_point_coordinates': [37.64015961, 55.73690033],
    'start_point_coordinates': [37.64015961, 55.73690033],
    'account_id': 999,
    'account_name': 'card',
    'car_id': '2d94007f-fb0a-46ee-8a73-da2105b7b61a',
    'commission_sum': '0.0',
    'drive_user_id': '3a896838-cdba-4d1c-9f34-af1bbb8232ae',
    'dt': '2020-04-12T13:50:50.000000Z',
    'duration': 24,
    'finished_at': '2020-04-12T13:50:50.000000Z',
    'model': 'kia_rio',
    'number': 'б491вг968',
    'orig_transaction_id': 'ef6b256f-6f80d00e-cef1f8ca-854e6112',
    'parent_id': 0,
    'promocode_sum': '0.00',
    'sequential_id': 46432,
    'service_order_id': '000',
    'started_at': '2020-04-12T13:00:00.000000Z',
    'tariff': 'Автотест _3',
    'timestamp': 1586699450000000,
    'total_mileage': 0,
    'total_sum': '100.00',
    'transaction_currency': 'RUB',
    'transaction_id': '000_2',
    'type': 'carsharing',
    'user_discount': 0,
}

TOPIC = {
    'namespace': 'corp',
    'topic': {'type': 'drive/rus', 'external_ref': '123', 'revision': 1},
    'events': [
        {
            'type': 'order_created',
            'meta_schema_version': 1,
            'occured_at': '2020-01-12T13:42:22.000000Z',
            'meta': {
                'transaction_id': '123_1',
                'client_external_ref': 'client_id',
            },
        },
    ],
}


class Context:
    def __init__(self):
        self.data = None

    def set_data(self, data):
        self.data = data


@pytest.fixture
def bills_context():
    return Context()


@pytest.fixture
def topics_context():
    return Context()


def geocoder_response(components):
    return {
        'features': [
            {
                'properties': {
                    'GeocoderMetaData': {
                        'Address': {
                            'Components': components,
                            'formatted': 'Россия, Москва, улица Панфёрова, 12',
                        },
                    },
                },
            },
        ],
    }


@pytest.mark.parametrize(
    'sessions, query',
    [
        pytest.param(
            [],
            {'limit': '50', 'billing_type': 'car_usage,toll_road'},
            id='empty_orders',
        ),
        pytest.param(
            [ADDITIONAL],
            {
                'until': '1586699450',
                'limit': '50',
                'billing_type': 'car_usage,toll_road',
            },
            id='found_orders',
        ),
    ],
)
@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_drive_no_orders(
        cron_context,
        mockserver,
        sessions,
        query,
        mock_refunds,
        mock_int_api,
        mock_topics,
        mock_events,
        mock_geocoder,
        mock_billing_replication,
):
    @mockserver.json_handler('/drive/api/b2b/bills/history')
    async def _bills(request):
        return {'cursor': 46433, 'sessions': sessions}

    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        assert request.query == query
        return {'cursor': 46433, 'sessions': []}

    try:
        await run_cron.main(
            ['corp_orders.crontasks.sync_drive_orders', '-t', '0'],
        )
    except exceptions.OrderUserNotFound:
        pass


@pytest.mark.parametrize(
    ['territories', 'error', 'error_text'],
    [
        pytest.param(
            {'_id': 'rus'},
            exceptions.VatNotFound,
            'Could not find vat for country rus',
            id='no_vat',
        ),
        pytest.param(
            {'_id': 'rus', 'vat': 'wrong'},
            exceptions.InvalidVat,
            'Vat wrong is invalid, country: rus',
            id='invalid_vat',
        ),
    ],
)
async def test_vat_failed(
        cron_context,
        mockserver,
        mock_bills,
        mock_refunds,
        mock_int_api,
        mock_geocoder,
        mock_billing_replication,
        territories,
        error,
        error_text,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _countries(request):
        return {'countries': [territories]}

    with pytest.raises(error) as exc:
        await run_cron.main(
            ['corp_orders.crontasks.sync_drive_orders', '-t', '0'],
        )

    assert error_text in str(exc)


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
@pytest.mark.parametrize(
    'components',
    [
        pytest.param([{'kind': 'locality', 'name': 'Москва'}], id='locality'),
        pytest.param(
            [
                {'kind': 'province', 'name': 'ЦАО'},
                {'kind': 'province', 'name': 'Москва'},
            ],
            id='province',
        ),
    ],
)
async def test_sync_drive_orders(
        cron_context,
        mockserver,
        mock_bills,
        mock_int_api,
        mock_topics,
        mock_events,
        mock_billing_replication,
        components,
):
    @mockserver.json_handler('/geocoder/yandsearch')
    async def _geocoder(request):
        return geocoder_response(components)

    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        return {'cursor': 46433, 'sessions': []}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])
    ctx = base_context.Context(cron_context, 'test_sync_drive_orders', {})
    master_pool = ctx.generated.pg.master[0]
    async with master_pool.acquire() as conn:
        orders_cursor = await conn.fetch(
            ctx.generated.postgres_queries['fetch_drive_bills_cursor.sql'],
        )
    assert orders_cursor[0]['cursor'] == 46433

    async with master_pool.acquire() as conn:
        order = await conn.fetchrow(
            'select city, finish_point_address, start_point_address, timezone '
            'from corp_orders.drive_orders limit 1;',
        )
    assert order['city'] == 'Москва'
    assert order['finish_point_address']
    assert order['start_point_address']
    assert order['timezone']


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_multiple_bills(
        cron_context,
        mockserver,
        mock_bills,
        bills_context,
        mock_refunds,
        mock_int_api,
        mock_topics,
        mock_events,
        load_json,
        mock_geocoder,
        mock_billing_replication,
):
    async def _get_order(order_id):
        ctx = base_context.Context(cron_context, 'test_sync_drive_orders', {})
        master_pool = ctx.generated.pg.master[0]
        async with master_pool.acquire() as conn:
            orders = await conn.fetch(
                ctx.generated.postgres_queries[
                    'fetch_drive_orders_by_ids.sql'
                ],
                [order_id],
            )
            return orders[0]

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])
    db_order = await _get_order('123')
    assert db_order['total_sum'] == '50.00'
    updated_at = db_order['updated_at']

    additional = copy.copy(ADDITIONAL)
    additional['account_id'] = 123
    additional['service_order_id'] = '123'
    additional['transaction_id'] = '123_3'
    additional['total_sum'] = '200.20'
    additional['duration'] = 123123123
    additional['finish_point_coordinates'] = [123.123, 456.456]
    bills_context.set_data(additional)

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])
    db_order = await _get_order('123')
    assert db_order['total_sum'] == '250.20'
    assert db_order['updated_at'] > updated_at
    assert db_order['duration'] == 123123123
    assert list(db_order['finish_point_coordinates']) == [123.123, 456.456]


@pytest.mark.config(
    CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'],
    CORP_SYNC_DRIVE_START_DATE='2020-04-01T00:00:00+00:00',
)
async def test_sync_unknown_account(
        cron_context,
        mockserver,
        load_json,
        mock_bills,
        bills_context,
        mock_refunds,
        mock_int_api,
        mock_topics,
        mock_geocoder,
        mock_billing_replication,
):
    bills_context.set_data(ADDITIONAL)

    with pytest.raises(exceptions.OrderUserNotFound) as exc:
        await run_cron.main(
            ['corp_orders.crontasks.sync_drive_orders', '-t', '0'],
        )

    assert 'Accounts users not found: [999]' in str(exc)


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_known_order_event(
        cron_context,
        mockserver,
        load_json,
        mock_bills,
        mock_refunds,
        mock_int_api,
        mock_geocoder,
        mock_topics,
        topics_context,
        mock_billing_replication,
):
    topics_context.set_data(TOPIC)

    @mockserver.json_handler('/corp-billing-events/v1/events')
    async def _events(request):
        events = request.json['events']
        assert len(events) == 1
        assert events[0]['external_ref'] == '123_2'
        assert events[0]['topic']['external_ref'] == '123'
        assert events[0]['topic']['type'] == 'drive/order'
        assert events[0]['type'] == 'price_changed'
        return {}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_unknown_order_event(
        cron_context,
        mockserver,
        load_json,
        mock_bills,
        mock_refunds,
        mock_int_api,
        mock_geocoder,
        mock_topics,
        topics_context,
        mock_billing_replication,
):
    @mockserver.json_handler('/corp-billing-events/v1/events')
    async def _events(request):
        events = request.json['events']
        assert len(events) == 4
        assert events[0]['external_ref'] == '123_1'
        assert events[0]['topic']['external_ref'] == '123_1'
        assert events[0]['topic']['type'] == 'drive/order'
        assert events[0]['meta']['order_external_ref'] == '123'
        return {}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_known_refund_event(
        cron_context,
        mockserver,
        load_json,
        mock_bills,
        mock_refunds,
        mock_int_api,
        mock_geocoder,
        mock_topics,
        topics_context,
        mock_billing_replication,
):
    topic = copy.copy(TOPIC)
    topic['events'][0]['meta']['transaction_id'] = '123_2'
    topic['events'][0]['type'] = 'price_changed'
    topic['events'][0]['occured_at'] = '2020-01-12T13:42:23.000000Z'

    topics_context.set_data(TOPIC)

    @mockserver.json_handler('/corp-billing-events/v1/events')
    async def _events(request):
        events = request.json['events']
        assert len(events) == 1
        assert events[0]['external_ref'] == '123_1'
        return {}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_sync_old_refund_event(
        cron_context,
        mockserver,
        patch,
        load_json,
        mock_bills,
        mock_refunds,
        mock_int_api,
        mock_events,
        mock_geocoder,
        mock_topics,
        topics_context,
        mock_billing_replication,
):
    topic = copy.copy(TOPIC)
    topic['events'][0]['meta']['transaction_id'] = 'existing'
    topic['events'][0]['type'] = 'price_changed'
    topic['events'][0]['occured_at'] = '2020-01-12T14:42:23+00:00'

    topics_context.set_data(topic)

    with pytest.raises(exceptions.OldDateRefund) as exc:
        await run_cron.main(
            ['corp_orders.crontasks.sync_drive_orders', '-t', '0'],
        )

    assert (
        'Transaction 123_1 2020-01-12T13:42:46+00:00 occurred earlier '
        'than the last event 2020-01-12T14:42:23+00:00' in str(exc)
    )


@pytest.mark.parametrize(
    'features',
    [
        pytest.param({'features': None}, id='type_error'),
        pytest.param(
            {
                'features': [
                    {'properties': {'GeocoderMetaData': {'Address': {}}}},
                ],
            },
            id='not_formatted',
        ),
    ],
)
@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_addresses_not_found(
        cron_context,
        mockserver,
        mock_bills,
        mock_int_api,
        mock_topics,
        mock_events,
        mock_billing_replication,
        features,
):
    @mockserver.json_handler('/geocoder/yandsearch')
    async def _geocoder(request):
        return features

    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        return {'cursor': 46433, 'sessions': []}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])
    ctx = base_context.Context(cron_context, 'test_sync_drive_orders', {})
    master_pool = ctx.generated.pg.master[0]
    async with master_pool.acquire() as conn:
        orders_cursor = await conn.fetch(
            ctx.generated.postgres_queries['fetch_drive_bills_cursor.sql'],
        )
    assert orders_cursor[0]['cursor'] == 46433

    async with master_pool.acquire() as conn:
        order = await conn.fetchrow(
            'select city, finish_point_address, start_point_address '
            'from corp_orders.drive_orders limit 1;',
        )
    assert order['city'] == ''
    assert order['finish_point_address'] == ''
    assert order['start_point_address'] == ''


@pytest.mark.parametrize(['contracts'], [pytest.param([], id='no_contracts')])
@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS=['client_id'])
async def test_contracts_not_found(
        cron_context,
        mockserver,
        mock_bills,
        mock_int_api,
        mock_topics,
        mock_geocoder,
        contracts,
):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    async def _contracts(request):
        return contracts

    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        return {'cursor': 46433, 'sessions': []}

    with pytest.raises(exceptions.InactiveClientOrder) as exc:
        await run_cron.main(
            ['corp_orders.crontasks.sync_drive_orders', '-t', '0'],
        )

    assert 'Clients contracts validation failed' in str(exc)


@pytest.mark.config(CORP_SYNC_DRIVE_ORDERS_CLIENTS_TO_SKIP=['client_id'])
async def test_skip_client(
        cron_context,
        mockserver,
        mock_bills,
        mock_int_api,
        mock_topics,
        mock_geocoder,
        mock_billing_replication,
):
    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        return {'cursor': 46433, 'sessions': []}

    @mockserver.json_handler('/corp-billing-events/v1/events')
    async def _events(request):
        # client skipped, order was not sent
        assert not request.json['events']
        return {}

    await run_cron.main(['corp_orders.crontasks.sync_drive_orders', '-t', '0'])


@pytest.fixture
def mock_bills(mockserver, load_json, bills_context):
    @mockserver.json_handler('/drive/api/b2b/bills/history')
    async def _bills(request):
        base = load_json('drive_data.json')['bills/history']
        if bills_context.data:
            base['sessions'].append(bills_context.data)
        return base

    return _bills


@pytest.fixture
def mock_refunds(mockserver, load_json, additional=None):
    @mockserver.json_handler('/drive/api/b2b/refunds/history')
    async def _refunds(request):
        base = load_json('drive_data.json')['refunds/history']
        if additional:
            base['sessions'].append(additional)
        return base

    return _refunds


@pytest.fixture
def mock_int_api(mockserver, load_json):
    @mockserver.json_handler('/taxi-corp-integration/v1/drive/info')
    async def _info(request):
        return load_json('corp_int_api_data.json')

    return _info


@pytest.fixture
def mock_topics(mockserver, load_json, topics_context):
    @mockserver.json_handler('/corp-billing-events/v1/topics/full')
    async def _topics(request):
        topics = []
        if topics_context.data:
            topics.append(topics_context.data)
        return {'topics': topics}

    return _topics


@pytest.fixture
def mock_events(mockserver):
    @mockserver.json_handler('/corp-billing-events/v1/events')
    async def _events(request):
        return {}

    return _events


@pytest.fixture
def mock_geocoder(mockserver, components=None):
    @mockserver.json_handler('/geocoder/yandsearch')
    async def _geocoder(request):
        return geocoder_response([{'kind': 'locality', 'name': 'Москва'}])

    return _geocoder


@pytest.fixture
def mock_billing_replication(mockserver, load_json):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    async def _contracts(request):
        return load_json('billing_replication_data.json')

    return _contracts
