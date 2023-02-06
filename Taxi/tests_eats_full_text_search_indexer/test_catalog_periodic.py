import pytest


def gen_place(place_id, business='shop'):
    return {
        'id': place_id,
        'slug': 'slug_{}'.format(place_id),
        'brand': {
            'id': 1,
            'slug': 'brand_slug_1',
            'name': 'brand_name',
            'picture_scale_type': 'aspect_fit',
        },
        'name': 'name_{}'.format(place_id),
        'business': business,
        'rating': {'admin': 5.0, 'count': 0, 'users': 0},
        'updated_at': '2020-10-26T14:14:22Z',
        'launched_at': '2020-10-26T00:00:00Z',
        'region': {'geobase_ids': [], 'id': 1, 'time_zone': ''},
        'enabled': place_id % 2 == 0,
        'revision_id': 1,
    }


UPDATES_LIMIT = 2
UPDATES_CORRECTION = 10
SERVICE = 'eats_fts'


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_CATALOG_STORAGE_PERIODIC={
        'full_update_interval': 7200,
        'incremental_update_interval': 3600,
        'updates_limit': UPDATES_LIMIT,
        'updates_correction': UPDATES_CORRECTION,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_PLACES_UPDATES_SETTINGS={
        'saas_settings': {
            'service_alias': SERVICE,
            'prefix': 2,
            'place_document_batch_size': 1,
        },
        'use_document_meta': True,
        'use_market_document_meta': True,
        'market_prefix': 42,
    },
)
async def test_catalog_storage_periodic(
        testpoint,
        taxi_eats_full_text_search_indexer,
        taxi_eats_full_text_search_indexer_monitor,
        mockserver,
        pgsql,
):
    """
    Проверяем, что периодик делает запрос в catalog-storage 3 раза.
    Проверяем, что плейс с business=store не попадает в базу.
    """

    @testpoint('components:catalog-storage-periodic-finished')
    def catalog_periodic_finished(arg):
        pass

    shop_places = list(gen_place(i) for i in range(3))
    non_shop_place = gen_place(1000, business='store')
    all_places = shop_places + [non_shop_place]

    # multiline path just to pass flake8
    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/places/updates'
        ),
    )
    def _catalog_storage(request):
        request_json = request.json
        assert request_json['limit'] == UPDATES_LIMIT
        # first request
        if request_json['last_known_revision'] == 0:
            return {
                'last_known_revision': 1,
                'places': [shop_places[0], non_shop_place],
            }
        # second request
        if request_json['last_known_revision'] == 1:
            return {'last_known_revision': 2, 'places': shop_places[1:3]}
        # third request
        if request_json['last_known_revision'] == 2:
            return {'last_known_revision': 2, 'places': []}
        return {'last_known_revision': 2, 'places': []}

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def _saas_push(request):
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

    metric = await taxi_eats_full_text_search_indexer_monitor.get_metric(
        'catalog_storage_statistics',
    )
    old_places_count = metric['got_places_count']
    expected_places_count = len(all_places)

    async with taxi_eats_full_text_search_indexer.spawn_task(
            'catalog-storage-periodic',
    ):
        result = await catalog_periodic_finished.wait_call()
        assert result['arg'] == expected_places_count

        # Тестируем метрики
        metric = await taxi_eats_full_text_search_indexer_monitor.get_metric(
            'catalog_storage_statistics',
        )
        new_places_count = metric['got_places_count']
        assert metric['has_error'] == 0
        assert new_places_count - old_places_count == expected_places_count

        cursor = pgsql['eats_full_text_search_indexer'].cursor()
        cursor.execute(
            """
            SELECT
                place_id,
                place_slug,
                enabled,
                brand_id
            FROM
                fts_indexer.place_state
            ORDER BY place_id
        """,
        )
        place_state_data = list(
            {
                'id': row[0],
                'slug': row[1],
                'enabled': row[2],
                'brand_id': row[3],
            }
            for row in cursor
        )

        assert len(place_state_data) == len(shop_places)

        for expected, actual in zip(shop_places, place_state_data):
            assert actual['brand_id'] == expected['brand']['id']
            del actual['brand_id']
            for key, value in actual.items():
                assert value == expected[key]

        cursor.execute(
            """
            SELECT
                last_revision
            FROM
                fts_indexer.catalog_state
            ORDER BY id
            LIMIT 1""",
        )
        last_revision = list(row[0] for row in cursor)[0]
        assert last_revision == 2


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_CATALOG_STORAGE_PERIODIC={
        'full_update_interval': 7200,
        'incremental_update_interval': 3600,
        'updates_limit': UPDATES_LIMIT,
        'updates_correction': UPDATES_CORRECTION,
    },
)
async def test_catalog_storage_periodic_fail(
        testpoint,
        taxi_eats_full_text_search_indexer,
        taxi_eats_full_text_search_indexer_monitor,
        mockserver,
        pgsql,
):
    """
    Проверяем поведение при ошибке в запросе к catalog-storage
    """

    @testpoint('components:catalog-storage-periodic-finished')
    def catalog_periodic_finished(arg):
        pass

    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/places/updates'
        ),
    )
    def _catalog_storage(request):
        return mockserver.make_response(status=500)

    expected_places_count = 0

    async with taxi_eats_full_text_search_indexer.spawn_task(
            'catalog-storage-periodic',
    ):
        result = await catalog_periodic_finished.wait_call()
        assert result['arg'] == expected_places_count

        # Тестируем метрики
        metric = await taxi_eats_full_text_search_indexer_monitor.get_metric(
            'catalog_storage_statistics',
        )
        places_count = metric['got_places_count']
        assert metric['has_error'] == 1
        assert places_count == expected_places_count

        cursor = pgsql['eats_full_text_search_indexer'].cursor()
        cursor.execute(
            """
            SELECT
                place_id,
                place_slug,
                enabled
            FROM
                fts_indexer.place_state
            ORDER BY place_id
        """,
        )
        place_state_data = list(
            {'place_id': row[0], 'place_slug': row[1], 'enabled': row[2]}
            for row in cursor
        )

        assert len(place_state_data) == expected_places_count
