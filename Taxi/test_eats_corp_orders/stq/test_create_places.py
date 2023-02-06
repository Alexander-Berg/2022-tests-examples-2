import pytest

from eats_corp_orders.stq import create_places


async def test_create_places(
        stq3_context, load_json, mock_eats_core_b2b, mock_eats_catalog_storage,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    async def _place_balance_client_id(request):
        assert set(request.json['place_ids']) == {'777'}
        return {'clients': [{'place_id': 777, 'client_balance_id': 777}]}

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _eats_catalog_storage_handler(request):
        assert set(request.json['place_ids']) == {777}
        return load_json('eats-catalog-storage.json')

    await create_places.task(stq3_context, place_ids=['777'])


async def test_create_places_error_core(
        stq3_context, load_json, mock_eats_core_b2b, mock_eats_catalog_storage,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    async def _place_balance_client_id(request):
        return {'clients': []}

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _eats_catalog_storage_handler(request):
        return load_json('eats-catalog-storage.json')

    with pytest.raises(create_places.ErrorCreatePlaces):
        await create_places.task(stq3_context, place_ids=['777'])


async def test_create_places_error_storage(
        stq3_context, mock_eats_core_b2b, mock_eats_catalog_storage,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    async def _place_balance_client_id(request):
        return {'clients': [{'place_id': 777, 'client_balance_id': 777}]}

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _eats_catalog_storage_handler(request):
        return {'places': []}

    with pytest.raises(create_places.ErrorCreatePlaces):
        await create_places.task(stq3_context, place_ids=['777'])
