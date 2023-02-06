# pylint: disable=unused-variable
import json

import pytest

from eats_integration_offline_orders.generated.cron import run_cron


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
@pytest.mark.config(
    EI_OFFLINE_ORDERS_PLACE_SYNC_SETTINGS={
        'batch_size': 1,
        'delay_seconds': 0,
        'newly_created_window_size_seconds': 3600,
    },
    TVM_RULES=[{'src': 'eats-integration-offline-orders', 'dst': 'personal'}],
)
@pytest.mark.now('2022-06-14T03:00:00.0+03:00')
async def test_sync_places(
        cron_context,
        pgsql,
        mock_eats_core_b2b,
        mock_eats_catalog_storage,
        mock_eats_core,
        mock_personal,
        load,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    def mock_place_balance_client_ids(request):
        clients = [
            {'place_id': 1, 'client_balance_id': 101},
            {'place_id': 2, 'client_balance_id': 102},
            {'place_id': 3, 'client_balance_id': 103},
        ]
        return {
            'clients': [
                client
                for client in clients
                if str(client['place_id']) in request.json['place_ids']
            ],
        }

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    def mock_search_places_list(request):
        return json.loads(load('catalog_storage_response.json'))

    @mock_eats_core('/v1/places', prefix=True)
    def mock_places_full_info(request):
        return json.loads(load('eats_core_response.json'))

    @mock_personal('/v1/tins/bulk_store')
    def personal_handler(request):
        value = request.json['items'][0]['value']
        assert value == '7707201970'
        return {'items': [{'id': 'personal_tin_id__3', 'value': value}]}

    def fetch_records_by_place_id():
        with pgsql['eats_integration_offline_orders'].dict_cursor() as cursor:
            cursor.execute('select * from restaurants;')
            records = cursor.fetchall()
            return {record['place_id']: record for record in records}

    await run_cron.main(
        [
            'eats_integration_offline_orders.crontasks.'
            'sync_places_newly_created',
            '-t',
            '0',
        ],
    )

    records_by_place_id = fetch_records_by_place_id()
    assert records_by_place_id['1']['billing_client_id'] == '101'
    assert records_by_place_id['2']['billing_client_id'] == '2'
    assert records_by_place_id['3']['billing_client_id'] is None
    assert records_by_place_id['2']['geo_point'] == '(39.022872,45.056503)'

    await run_cron.main(
        [
            'eats_integration_offline_orders.crontasks.sync_places_full',
            '-t',
            '0',
        ],
    )

    records_by_place_id = fetch_records_by_place_id()
    assert records_by_place_id['1']['billing_client_id'] == '101'
    assert records_by_place_id['2']['billing_client_id'] == '102'
    assert records_by_place_id['2']['region_id'] == 13
    assert records_by_place_id['3']['billing_client_id'] == '103'
    assert records_by_place_id['3']['personal_tin_id'] == 'personal_tin_id__3'
