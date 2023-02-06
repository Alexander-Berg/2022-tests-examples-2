async def test_get_ts_ok(web_app_client, cache_shield, load_json):
    response = await web_app_client.get(
        '/v1/tariff_settings/bulk_retrieve',
        params={'zone_names': 'moscow,tel_aviv'},
    )

    data = await response.json()
    assert response.status == 200

    assert data == {
        'zones': [
            {'zone': 'moscow', 'tariff_settings': load_json('moscow.json')},
            {'zone': 'tel_aviv', 'status': 'not_found'},
        ],
    }
