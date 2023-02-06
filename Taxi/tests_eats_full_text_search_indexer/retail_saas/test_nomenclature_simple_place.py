import pytest


SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 1
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2


@pytest.mark.config()
@pytest.mark.parametrize('saas_service_send_to', ('eats_retail_search', 'all'))
@pytest.mark.parametrize(
    'track_document_changes, saas_times_called_diff',
    (
        pytest.param(True, 0, id='track document changes'),
        pytest.param(False, 2, id='do not track document changes'),
    ),
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_simple_place(
        taxi_eats_full_text_search_indexer,
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        # parametrize,
        saas_service_send_to,
        track_document_changes,
        saas_times_called_diff,
):
    """
    Проверяем отправку простого плейса из номенклатуры в
    saas
    плейс с 1 категорией в которой 1 товар
    проверяем что при повтором запуски задачи в saas ничего не
    отправляется (из-за хэшей) в первом кейсе и
    происходит переотправка документов во втором
    """

    set_retail_settings(
        saas_service_send_to=saas_service_send_to,
        track_document_changes=track_document_changes,
    )

    place_id = '1'
    place_slug = 'place_slug'

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def nmn_assortment_names(request):
        assert request.query['place_id'] == place_id
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def nmn_categories(request):
        assert request.query['place_id'] == place_id
        assert request.query['assortment_name'] == 'partner'
        assert not request.json['category_ids']
        return load_json('nomenclature_categories_response.json')

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def nmn_products(request):
        response = load_json('nomenclature_products_response.json')
        assert set(request.json['product_ids']) == {
            p['id'] for p in response['products']
        }

        return response

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_FTS_SERVICE),
    )
    def _saas_fts_push(request):
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
        payload = request.json
        prefix = payload['prefix']
        if prefix == SAAS_RETAIL_SEARCH_ITEMS_PREFIX:  # item
            expected_payload = load_json('saas_item.json')
            assert payload == expected_payload
        elif prefix == SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX:  # category
            assert payload == load_json('saas_category_1.json')
        else:
            assert False, 'Unknown prefix {}'.format(prefix)
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

    assert nmn_assortment_names.times_called == 1
    assert nmn_categories.times_called == 1
    assert nmn_products.times_called == 1
    assert saas_retail_search_push.times_called == 2  # category + item

    first_saas_times_called = saas_retail_search_push.times_called

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    assert nmn_assortment_names.times_called == 2
    assert nmn_categories.times_called == 2
    assert nmn_products.times_called == 2
    assert (
        saas_retail_search_push.times_called - first_saas_times_called
        == saas_times_called_diff
    )  # не изменилось
