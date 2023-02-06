import pytest


FTS_SERVICE = 'eats_fts'
RETAIL_SEARCH_SERVICE = 'eats_retail_search'
PREFIX = 1


@pytest.mark.parametrize('saas_service_send_to', ('eats_fts', 'all'))
@pytest.mark.parametrize('nmn_integration_version', ('v1', 'v2'))
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_inner_category(
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        nmn_integration_version,
        saas_service_send_to,
):
    """
    Проверяем отправку вложенных категорий
    номенклатура возвращает структуру вида
    category_1
      - category_2
          - item_1
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
        category_id = int(request.query.get('category_id') or 0)
        if category_id:
            if category_id == 1:  # root category
                return load_json('nomenclature_category_1.json')
            assert False, 'Unknown category_id {}'.format(category_id)
        return load_json('nomenclature_category_root.json')

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
        '/saas-push/push/{service}'.format(service=FTS_SERVICE),
    )
    def saas_push(request):
        payload = request.json
        doc_type = payload['docs'][0]['i_type']['value']
        if doc_type == 1:  # item
            assert payload == load_json('saas_item_1.json')
        elif doc_type == 2:  # category
            category_id = payload['docs'][0]['i_category_id']['value']
            if category_id == 1:
                assert payload == load_json('saas_category_1.json')
            elif category_id == 2:
                assert payload == load_json('saas_category_2.json')
            else:
                assert False, 'Unknown category_id {}'.format(category_id)
        else:
            assert False, 'Unknown document type {}'.format(doc_type)
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
        '/saas-push/push/{service}'.format(service=RETAIL_SEARCH_SERVICE),
    )
    def _saas_retail_search_push(request):
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

    if nmn_integration_version == 'v1':
        assert nomenclature.times_called == 2  # root category + first category
    else:
        assert nmn_assortment_names.times_called == 1
        assert nmn_categories.times_called == 1
        assert nmn_products.times_called == 1
    assert saas_push.times_called == 3  # 2 category + item
