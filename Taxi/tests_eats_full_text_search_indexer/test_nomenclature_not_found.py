import pytest


FTS_SERVICE = 'eats_fts'
RETAIL_SEARCH_SERVICE = 'eats_retail_search'
PREFIX = 1


@pytest.mark.parametrize('saas_service_send_to', ('eats_fts', 'all'))
@pytest.mark.parametrize('nmn_integration_version', ('v1', 'v2'))
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_not_found(
        mockserver,
        stq_runner,
        set_retail_settings,
        saas_service_send_to,
        nmn_integration_version,
):
    """
    Проверяем поведение stq задачи индексации данных
    из номенклатуры при 404
    """

    set_retail_settings(
        saas_service_send_to=saas_service_send_to,
        integration_version=nmn_integration_version,
    )

    place_slug = 'place_slug'
    place_id = '1'

    @mockserver.json_handler('eats-nomenclature/v1/nomenclature')
    def nomenclature(request):
        assert request.query['slug'] == place_slug
        return mockserver.make_response(status=404, json={})

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def nmn_assortment_names(request):
        assert request.query['place_id'] == place_id
        return mockserver.make_response(status=404, json={})

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def nmn_categories(request):
        assert False, 'Should be unreachable'

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def nmn_products(request):
        assert False, 'Should be unreachable'

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=FTS_SERVICE),
    )
    def saas_push(request):
        assert False, 'Should be unreachable'

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=RETAIL_SEARCH_SERVICE),
    )
    def _saas_retail_search_push(request):
        assert False, 'Should be unreachable'

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    if nmn_integration_version == 'v1':
        assert nomenclature.times_called == 1
    else:
        assert nmn_assortment_names.times_called == 1
        assert nmn_categories.times_called == 0
        assert nmn_products.times_called == 0
    assert saas_push.times_called == 0
