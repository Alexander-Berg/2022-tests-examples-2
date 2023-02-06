import pytest


SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 1
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2


@pytest.mark.parametrize('saas_service_send_to', ('eats_retail_search', 'all'))
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_not_found(
        mockserver,
        stq_runner,
        set_retail_settings,
        # parametrize
        saas_service_send_to,
):
    """
    Проверяем поведение stq задачи индексации данных
    из номенклатуры при 404
    """

    set_retail_settings(saas_service_send_to=saas_service_send_to)

    place_slug = 'place_slug'
    place_id = '1'

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
        '/saas-push/push/{service}'.format(service=SAAS_FTS_SERVICE),
    )
    def _saas_fts_push(request):
        assert False, 'Should be unreachable'

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def saas_retail_search_push(request):
        assert False, 'Should be unreachable'

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    assert nmn_assortment_names.times_called == 1
    assert nmn_categories.times_called == 0
    assert nmn_products.times_called == 0
    assert saas_retail_search_push.times_called == 0
