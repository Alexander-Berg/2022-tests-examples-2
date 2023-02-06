import json

import pytest


FTS_SERVICE = 'eats_fts'
RETAIL_SEARCH_SERVICE = 'eats_retail_search'
PREFIX = 1


@pytest.mark.parametrize('saas_service_send_to', ('eats_fts', 'all'))
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_assortments_merge(
        mockserver,
        stq_runner,
        load_json,
        set_retail_settings,
        saas_service_send_to,
):
    set_retail_settings(saas_service_send_to=saas_service_send_to)

    place_slug = 'place_slug'
    place_id = '1'

    expected_assortment_names = ['partner', 'custom', 'not_parsed']
    expected_product_ids = ['public_item_1', 'public_item_2', 'public_item_3']
    expected_category_ids = [1, 2, 3, 4, 5]

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def nmn_assortment_names(request):
        assert request.query['place_id'] == place_id
        return {
            'assortments': [
                {'name': name} for name in expected_assortment_names
            ],
        }

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def nmn_categories(request):
        assert request.query['place_id'] == place_id
        assert not request.json['category_ids']

        assortment_name = request.query['assortment_name']
        assert assortment_name in expected_assortment_names
        if assortment_name == 'not_parsed':
            return mockserver.make_response(status=404, json={})

        return load_json(
            f'nomenclature_categories_{assortment_name}_response.json',
        )

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def nmn_products(request):
        response = load_json('nomenclature_products_response.json')
        assert set(request.json['product_ids']) == set(expected_product_ids)

        return response

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=FTS_SERVICE),
    )
    def saas_push(request):
        payload = request.json
        doc_type = payload['docs'][0]['i_type']['value']
        if doc_type == 1:  # item
            item_public_id = payload['docs'][0]['s_nom_item_id']['value']
            assert (
                item_public_id in expected_product_ids
            ), f'Unknown item public id {item_public_id}'
            assert sort_item_payload(payload) == sort_item_payload(
                load_json(f'saas_item_{item_public_id}.json'),
            )
        elif doc_type == 2:  # category
            category_id = payload['docs'][0]['i_category_id']['value']
            assert (
                category_id in expected_category_ids
            ), f'Unknown category_id {category_id}'
            assert payload == load_json(f'saas_category_{category_id}.json')
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

    assert nmn_assortment_names.times_called == 1
    assert nmn_categories.times_called == len(expected_assortment_names)
    assert nmn_products.times_called == 1
    assert saas_push.times_called == len(
        expected_category_ids + expected_product_ids,
    )


def sort_item_payload(payload):
    value = json.loads(payload['docs'][0]['s_categories']['value'])
    value.sort()
    payload['docs'][0]['s_categories']['value'] = json.dumps(value)

    value = json.loads(payload['docs'][0]['s_parent_categories_v2']['value'])
    value.sort(key=lambda k: k['id'])
    payload['docs'][0]['s_parent_categories_v2']['value'] = json.dumps(value)

    return payload
