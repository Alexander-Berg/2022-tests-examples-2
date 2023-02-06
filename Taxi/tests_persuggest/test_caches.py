import pytest


@pytest.mark.config(EDA_CATALOG_POLYGONS_CACHE_ENABLED=True)
async def test_eda_catalog_polygons_cache(
        taxi_persuggest, mockserver, load_json,
):
    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        return load_json('eats_regions_response.json')

    catalog_polygons = load_json('eda_catalog_polygons_response.json')
    requested_regions = []

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_catalog(request):
        region_id = request.query.get('eatsRegionId')
        requested_regions.append(region_id)

        return catalog_polygons[region_id]

    await taxi_persuggest.invalidate_caches(
        clean_update=False, cache_names=['eda-catalog-polygons'],
    )
    assert set(requested_regions) == {'1', '135'}
