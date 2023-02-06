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
async def test_nomenclature_inner_category(
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        # parametrize
        saas_service_send_to,
):
    """
    Проверяем отправку вложенных категорий
    номенклатура возвращает структуру вида
    category_1
      - category_2
          - item_1
    """

    set_retail_settings(saas_service_send_to=saas_service_send_to)

    place_slug = 'place_slug'
    place_id = '1'

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
            expected_item = load_json('saas_item.json')
            expected_item['docs'][0]['z_categories'][
                'value'
            ] = 'Second Category. First Category'
            assert payload == expected_item
        elif prefix == SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX:  # category
            category_id = payload['docs'][0]['i_category_id']['value']
            if category_id == 1:
                assert payload == load_json('saas_category_1.json')
            elif category_id == 2:
                assert payload == load_json('saas_category_2.json')
            else:
                assert False, 'Unknown category_id {}'.format(category_id)
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
    assert saas_retail_search_push.times_called == 3  # 2 category + item
