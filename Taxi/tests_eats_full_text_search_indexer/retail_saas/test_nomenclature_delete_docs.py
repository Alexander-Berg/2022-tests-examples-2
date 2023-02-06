import pytest

SAAS_FTS_SERVICE = 'eats_fts'
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1


# Использование таблицы с метаинформацией включается опцией use_document_meta
# Во включенном состоянии ожидаем что в конце работы таски
# в saas будет 3 запроса 2 на добавление и 1 на удаление,
# а в бд останется 2 документа
# (тот что нужно удалить из saas, удалится и из бд)
# В выключенном состоянии в saas будет два запроса (только добавление)
# а таблица останется неизмененной


@pytest.mark.parametrize('saas_service_send_to', ('eats_retail_search', 'all'))
@pytest.mark.parametrize('enable_pagination', (True, False))
@pytest.mark.parametrize('track_document_changes', (False, True))
@pytest.mark.parametrize(
    'use_document_meta, saas_push_called, final_db_urls_count',
    ((True, 4, 2), (False, 2, 4)),
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['create_place_state.sql', 'pg_eats_full_text_search_indexer.sql'],
)
async def test_nomenclature_delete_docs(
        taxi_eats_full_text_search_indexer,
        mockserver,
        stq_runner,
        load_json,
        pgsql,
        taxi_config,
        set_retail_settings,
        # parametrize
        saas_service_send_to,
        enable_pagination,
        track_document_changes,
        use_document_meta,
        saas_push_called,
        final_db_urls_count,
):
    """
    Проверяем удаление документов из saas
    для этого заполняем базу (fts_indexer.retail_document_meta)
    информацией о документах
    place_slug/categories/1
    place_slug/categories/2
    place_slug/items/1
    place_slug/items/2
    В ответе номенклатуры возвращаем только place_slug/categories/1
    и place_slug/items/1
    ожидаем delete для place_slug/categories/2 и place_slug/items/2

    Проверяем что track_document_changes при любом значении
    не влияет на удаление документов
    """

    set_retail_settings(
        saas_service_send_to=saas_service_send_to,
        use_document_meta=use_document_meta,
        track_document_changes=track_document_changes,
    )
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_INDEXER_RETAIL_DOCUMENT_META_SETTINGS': {
                'slice_size': 2,
                'select_slice_size': 2,
                'enable_pagination': enable_pagination,
            },
        },
    )

    await taxi_eats_full_text_search_indexer.invalidate_caches()

    place_slug = 'place_slug'
    place_id = '1'

    old_retail_doc_meta_urls = get_doc_meta_urls(pgsql)
    assert len(old_retail_doc_meta_urls) == 4

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
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def saas_retail_search_push(request):
        payload = request.json
        prefix = payload['prefix']
        if prefix == SAAS_RETAIL_SEARCH_ITEMS_PREFIX:  # item
            if payload['action'] == 'modify':
                assert payload == load_json('saas_item.json')
            elif payload['action'] == 'delete':
                assert payload['docs'][0]['url'] == '/1/items/public_item_2'
        elif prefix == SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX:  # category
            if payload['action'] == 'modify':
                assert payload == load_json('saas_category_1.json')
            elif payload['action'] == 'delete':
                assert payload['docs'][0]['url'] == '/place_slug/categories/2'
        else:
            assert False, 'Unknown document prefix {}'.format(prefix)
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

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id='id_1', kwargs={'place_slug': place_slug},
    )

    assert nmn_assortment_names.times_called == 1
    assert nmn_categories.times_called == 1
    assert nmn_products.times_called == 1

    retail_doc_meta_urls = get_doc_meta_urls(pgsql)
    assert (
        saas_retail_search_push.times_called == saas_push_called
    )  # category + item + delete
    assert len(retail_doc_meta_urls) == final_db_urls_count
    assert '/place_slug/categories/1' in retail_doc_meta_urls
    assert '/1/items/public_item_1' in retail_doc_meta_urls


def get_doc_meta_urls(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
        SELECT url
        FROM fts_indexer.retail_document_meta;
    """,
    )
    return {row[0] for row in cursor}
