import pytest

from eats_corp_orders.generated.cron import run_cron


async def test_sync_places(
        cron_context, mock_eats_core_b2b, mock_eats_catalog_storage, load_json,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    async def _place_balance_client_id(request):
        assert set(request.json['place_ids']) == {'1', '2'}
        return {
            'clients': [
                {'place_id': 1, 'client_balance_id': 1},
                {'place_id': 2, 'client_balance_id': 2},
            ],
        }

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _eats_catalog_storage_handler(request):
        assert set(request.json['place_ids']) == {1, 2}
        return load_json('eats-catalog-storage.json')

    with pytest.raises(Exception):
        await run_cron.main(
            ['eats_corp_orders.crontasks.sync_places', '-t', '0'],
        )

    place_1 = await cron_context.queries.places.get_by_id('1')
    assert place_1.serialize() == load_json('result_place_1.json')

    place_2 = await cron_context.queries.places.get_by_id('2')
    assert place_2.serialize() == load_json('result_place_2.json')
