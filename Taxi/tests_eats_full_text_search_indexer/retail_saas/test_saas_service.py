import pytest


SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 1
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1


@pytest.mark.config()
@pytest.mark.parametrize('nmn_integration_version', ('v1', 'v2'))
@pytest.mark.parametrize(
    'saas_service_send_to', ('eats_fts', 'eats_retail_search', 'all'),
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_saas_service(
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        nmn_integration_version,
        saas_service_send_to,
):
    """
    Проверяем, что документы отправляются в нужный сервис saas
    в зависимости от параметров конфига
    """

    set_retail_settings(
        saas_service_send_to=saas_service_send_to,
        integration_version=nmn_integration_version,
    )

    place_id = '1'
    place_slug = 'place_slug'

    @mockserver.json_handler('eats-nomenclature/v1/nomenclature')
    def _nomenclature(request):
        assert request.query['slug'] == place_slug
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def _nmn_assortment_names(request):
        assert request.query['place_id'] == place_id
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _nmn_categories(request):
        assert request.query['place_id'] == place_id
        assert request.query['assortment_name'] == 'partner'
        assert not request.json['category_ids']
        return load_json('nomenclature_categories_response.json')

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _nmn_products(request):
        response = load_json('nomenclature_products_response.json')
        assert set(request.json['product_ids']) == {
            p['id'] for p in response['products']
        }

        return response

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_FTS_SERVICE),
    )
    def saas_fts_push(request):
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def saas_retail_search_push(request):
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    assert saas_fts_push.has_calls == (
        saas_service_send_to in {'eats_fts', 'all'}
    )
    assert saas_retail_search_push.has_calls == (
        (saas_service_send_to in {'eats_retail_search', 'all'})
        and nmn_integration_version == 'v2'
    )


@pytest.mark.parametrize('brand_id_is_set', (True, False))
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_product_score(
        taxi_eats_full_text_search_indexer,
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        pgsql,
        brand_id_is_set,
):
    """
    Проверяем отправку скорингов товаров
    """

    set_retail_settings(saas_service_send_to='eats_retail_search')

    place_slug = 'place_slug'
    place_id = 1
    brand_id = 1

    if brand_id_is_set:
        set_brand_id(pgsql, place_id, brand_id)

    product_score = 0.027
    set_product_score(pgsql, brand_id, 'item_1', product_score)

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def _nmn_assortment_names(request):
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _nmn_categories(request):
        return load_json('nomenclature_categories_response.json')

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _nmn_products(request):
        return load_json('nomenclature_products_response.json')

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def saas_retail_search_push(request):
        payload = request.json
        prefix = payload['prefix']
        if prefix == SAAS_RETAIL_SEARCH_ITEMS_PREFIX:  # item
            assert len(payload['docs']) == 1
            assert ('f_buy_score' in payload['docs'][0]) == brand_id_is_set
            if brand_id_is_set:
                assert (
                    payload['docs'][0]['f_buy_score']['value'] == product_score
                )
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    assert saas_retail_search_push.times_called == 2


def set_brand_id(pgsql, place_id, brand_id):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
        UPDATE fts_indexer.place_state
        SET brand_id = {brand_id}
        WHERE place_id = {place_id}
    """,
    )


def set_product_score(pgsql, brand_id, origin_id, score):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
        INSERT INTO fts_indexer.product_scores (
            brand_id, origin_id, score
        ) VALUES (
            {brand_id}, '{origin_id}', {score}
        )
    """,
    )
