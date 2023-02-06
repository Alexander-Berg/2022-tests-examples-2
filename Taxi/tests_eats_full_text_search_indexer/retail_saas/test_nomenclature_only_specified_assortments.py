import pytest


SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 1
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2


@pytest.mark.parametrize('saas_service_send_to', ('eats_retail_search', 'all'))
@pytest.mark.parametrize(
    'assortment_names, expected_product_ids, expected_category_ids',
    (
        ([], ['public_item_1', 'public_item_2'], [3]),
        (['assortment_name_1'], ['public_item_1', 'public_item_2'], [1, 3]),
        (
            ['assortment_name_1', 'assortment_name_2'],
            ['public_item_1', 'public_item_2', 'public_item_3'],
            [1, 2, 3],
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_nomenclature_only_specified_assortments(
        mockserver,
        stq_runner,
        load_json,
        pgsql,
        set_retail_settings,
        # parametrize
        saas_service_send_to,
        assortment_names,
        expected_product_ids,
        expected_category_ids,
):
    brand_id = 1

    set_retail_settings(
        saas_service_send_to=saas_service_send_to,
        index_only_default_assortment=True,
        assortment_names_to_index_per_brand={brand_id: assortment_names},
    )

    place_slug = 'place_slug'
    place_id = '1'

    set_brand_id(pgsql, place_id=place_id, brand_id=brand_id)

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def nmn_assortment_names(request):
        assert False, 'Should be unreachable'

    requested_assortments = set()

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def nmn_categories(request):
        assert request.query['place_id'] == place_id
        assert not request.json['category_ids']
        assortment_to_categories_file = {
            'assortment_name_1': 'nomenclature_categories_response_1.json',
            'assortment_name_2': 'nomenclature_categories_response_2.json',
            None: 'nomenclature_categories_response_3.json',
        }
        request_assortment_name = None
        if 'assortment_name' in request.query:
            request_assortment_name = request.query['assortment_name']
        requested_assortments.add(request_assortment_name)
        return load_json(
            assortment_to_categories_file[request_assortment_name],
        )

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def nmn_products(request):
        assert set(request.json['product_ids']) == set(expected_product_ids)
        return load_json('nomenclature_products_response.json')

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
            item_public_id = payload['docs'][0]['p_public_id']['value']
            assert (
                item_public_id in expected_product_ids
            ), f'Unknown item public id {item_public_id}'
        elif prefix == SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX:  # category
            category_id = payload['docs'][0]['i_category_id']['value']
            assert (
                category_id in expected_category_ids
            ), f'Unknown category_id {category_id}'
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

    assert not nmn_assortment_names.times_called
    assert nmn_categories.times_called == len(assortment_names) + 1
    assert requested_assortments == set(assortment_names + [None])
    assert nmn_products.times_called == 1
    assert saas_retail_search_push.times_called == len(
        expected_category_ids + expected_product_ids,
    )


def set_brand_id(pgsql, place_id, brand_id):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
        UPDATE fts_indexer.place_state
        SET brand_id = {brand_id}
        WHERE place_id = {place_id}
    """,
    )
