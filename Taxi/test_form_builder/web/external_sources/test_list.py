async def test_external_sources_list(taxi_form_builder_web):
    response = await taxi_form_builder_web.get(
        '/v1/external-sources/builder/list/',
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'external_sources': [
            {
                'id': 'cars_brands_suggests',
                'name': 'cars_brands_suggests',
                'extra_kwargs_keys': [],
            },
            {
                'id': 'cars_models_suggests',
                'name': 'cars_models_suggests',
                'extra_kwargs_keys': ['brand'],
            },
            {
                'id': 'dadata_bank_suggests',
                'name': 'dadata_bank_suggests',
                'extra_kwargs_keys': [],
            },
            {
                'id': 'dadata_suggests',
                'name': 'dadata_suggests',
                'extra_kwargs_keys': [],
            },
            {
                'id': 'geo_suggests_city',
                'name': 'geo_suggests_city',
                'extra_kwargs_keys': ['countries', 'country_ids'],
            },
        ],
    }
