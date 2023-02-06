async def test_admin_terminal_create(
        taxi_eats_corp_orders_web,
        mock_eats_core_b2b,
        mock_eats_catalog_storage,
        load_json,
):
    @mock_eats_core_b2b('/v1/place/balance-client-ids')
    async def _place_balance_client_id(request):
        assert set(request.json['place_ids']) == {'888'}
        return {'clients': [{'place_id': 888, 'client_balance_id': 888}]}

    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _eats_catalog_storage_handler(request):
        assert set(request.json['place_ids']) == {888}
        return load_json('eats-catalog-storage.json')

    response = await taxi_eats_corp_orders_web.post(
        '/v1/admin/terminal',
        headers={'X-Idempotency-Token': ' X-Idempotency-Token'},
        json={'place_id': '888'},
    )
    assert response.status == 200
    content = await response.json()
    assert content.get('terminal_token')
    assert content.get('place_id') == '888'
