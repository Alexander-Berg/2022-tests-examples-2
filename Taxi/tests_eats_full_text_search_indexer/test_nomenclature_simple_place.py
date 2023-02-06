import pytest


FTS_SERVICE = 'eats_fts'
RETAIL_SEARCH_SERVICE = 'eats_retail_search'
PREFIX = 1


@pytest.mark.config()
@pytest.mark.parametrize('saas_service_send_to', ('eats_fts', 'all'))
@pytest.mark.parametrize('nmn_integration_version', ('v1', 'v2'))
@pytest.mark.parametrize(
    'nmn_integration_version_per_place',
    (
        pytest.param({}, id='no per place override'),
        pytest.param({'1': 'v1'}, id='v1 per place override'),
        pytest.param({'1': 'v2'}, id='v2 per place override'),
        pytest.param({'2': 'v2'}, id='different place override'),
    ),
)
@pytest.mark.parametrize(
    'track_document_changes,saas_times_called_diff',
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
        track_document_changes,
        saas_times_called_diff,
        saas_service_send_to,
        nmn_integration_version,
        nmn_integration_version_per_place,
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
        store_price=True,
        track_document_changes=track_document_changes,
        integration_version=nmn_integration_version,
        integration_version_per_place=nmn_integration_version_per_place,
    )

    place_id = '1'
    place_slug = 'place_slug'
    resolved_nmn_integration_ver = nmn_integration_version
    if place_id in nmn_integration_version_per_place:
        resolved_nmn_integration_ver = nmn_integration_version_per_place[
            place_id
        ]

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    @mockserver.json_handler('eats-nomenclature/v1/nomenclature')
    def nomenclature(request):
        assert request.query['slug'] == place_slug
        return load_json('nomenclature_response.json')

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
            expected_payload = load_json('saas_request_item.json')
            if resolved_nmn_integration_ver == 'v2':
                # v2 uses dummy price value
                expected_payload['docs'][0]['price']['value'] = '9999'
            assert payload == expected_payload
        elif doc_type == 2:  # category
            assert payload == load_json('saas_request_category.json')
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

    if resolved_nmn_integration_ver == 'v1':
        assert nomenclature.times_called == 2  # root category + first category
    else:
        assert nmn_assortment_names.times_called == 1
        assert nmn_categories.times_called == 1
        assert nmn_products.times_called == 1
    assert saas_push.times_called == 2  # category + item

    first_saas_times_called = saas_push.times_called

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    if resolved_nmn_integration_ver == 'v1':
        assert nomenclature.times_called == 4  # запросили повторно
    else:
        assert nmn_assortment_names.times_called == 2
        assert nmn_categories.times_called == 2
        assert nmn_products.times_called == 2
    assert (
        saas_push.times_called - first_saas_times_called
        == saas_times_called_diff
    )  # не изменилось
