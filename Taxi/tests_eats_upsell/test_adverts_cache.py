import pytest

from . import configs


CACHE_NAME = 'adverts-cache'
CACHE_UPDATE_FINISHED = 'adverts-cache-update-finished'
CACHE_METRIC_NAME = 'adverts-cache'

YT_DATA_TABLES = [
    'yt_promo_retail1.yaml',
    'yt_promo_rest1.yaml',
    'yt_promo_rest2.yaml',
]

YT_INC_DATA_TABLES = ['yt_promo_inc1.yaml', 'yt_promo_inc2.yaml']
YT_INC_TABLE_PATHS = [
    '//home/eda/promo/rest-incremental1',
    '//home/eda/promo/rest-incremental2',
]


@configs.adverts_cache_config(tables=[])
async def test_adverts_cache_no_tables(taxi_eats_upsell, testpoint):
    """
    Тест проверяет что кэш считается успешно обновленным, даже
    если в конфиге не указано ни одной таблицы
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    await taxi_eats_upsell.enable_testpoints()
    cache_data = await cache_update_finished.wait_call()
    assert cache_data['arg'] == {'restaurant_promos': [], 'retail_promos': []}


@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            '//home/eda/promo/retail1', 'promo1', configs.YtTableType.Retail,
        ),
        configs.YtTable(
            '//home/eda/promo/rest1',
            'promo2',
            configs.YtTableType.Restaurants,
        ),
        configs.YtTable(
            '//home/eda/promo/rest2',
            'promo3',
            configs.YtTableType.Restaurants,
        ),
    ],
)
@pytest.mark.yt(static_table_data=YT_DATA_TABLES)
async def test_adverts_cache_full_update(
        taxi_eats_upsell, testpoint, yt_apply,
):
    """
    Тест проверяет валидность полного обновления кэша
    промо компаний
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    await taxi_eats_upsell.enable_testpoints()
    cache_data = await cache_update_finished.wait_call()
    assert cache_data['arg']['restaurant_promos'] == [
        {
            'promotion_name': 'promo3',
            'table_path': 'hahn.//home/eda/promo/rest2',
            'promo_places': [
                {'place_id': 1005, 'promo_items': [{'core_id': 6}]},
            ],
        },
        {
            'promotion_name': 'promo2',
            'table_path': 'hahn.//home/eda/promo/rest1',
            'promo_places': [
                {'place_id': 1003, 'promo_items': [{'core_id': 4}]},
                {'place_id': 1004, 'promo_items': [{'core_id': 5}]},
            ],
        },
    ]
    assert cache_data['arg']['retail_promos'] == [
        {
            'promotion_name': 'promo1',
            'table_path': 'hahn.//home/eda/promo/retail1',
            'promo_places': [
                {
                    'place_id': 1001,
                    'promo_items': [
                        {'public_id': 'item1', 'suitable_categories': []},
                        {'public_id': 'item2', 'suitable_categories': []},
                    ],
                },
                {
                    'place_id': 1002,
                    'promo_items': [
                        {'public_id': 'item3', 'suitable_categories': []},
                    ],
                },
            ],
        },
    ]


@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            path=YT_INC_TABLE_PATHS[0],
            promotion='promo1',
            type=configs.YtTableType.Restaurants,
        ),
        configs.YtTable(
            path=YT_INC_TABLE_PATHS[1],
            promotion='promo2',
            type=configs.YtTableType.Restaurants,
        ),
    ],
)
@pytest.mark.yt(static_table_data=YT_INC_DATA_TABLES)
async def test_adverts_cache_incrementral_update(
        taxi_eats_upsell, testpoint, yt_apply, yt_client,
):
    """
    Тест проверяет валидность инкрементального обновления кэша
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    # skip testpoint call on initial cache update
    await taxi_eats_upsell.enable_testpoints()
    await cache_update_finished.wait_call()

    place_id = 1000
    brand_id = 100

    expected_rest_promos = [
        {
            'promotion_name': 'promo2',
            'table_path': 'hahn.//home/eda/promo/rest-incremental2',
            'promo_places': [
                {'place_id': place_id, 'promo_items': [{'core_id': 2}]},
            ],
        },
        {
            'promotion_name': 'promo1',
            'table_path': 'hahn.//home/eda/promo/rest-incremental1',
            'promo_places': [
                {'place_id': place_id, 'promo_items': [{'core_id': 1}]},
            ],
        },
    ]

    # full update
    await taxi_eats_upsell.invalidate_caches(
        clean_update=True, cache_names=[CACHE_NAME],
    )
    cache_data = await cache_update_finished.wait_call()
    assert cache_data['arg']['restaurant_promos'] == expected_rest_promos
    assert cache_data['arg']['retail_promos'] == []

    # modify the content of the second table
    yt_client.write_table(
        YT_INC_TABLE_PATHS[1],
        [
            {'brand_id': brand_id, 'place_id': place_id, 'core_item_id': 2},
            {'brand_id': brand_id, 'place_id': place_id, 'core_item_id': 3},
        ],
    )
    expected_rest_promos[0]['promo_places'][0]['promo_items'].append(
        {'core_id': 3},
    )

    # incremental udpate
    await taxi_eats_upsell.invalidate_caches(
        clean_update=False, cache_names=[CACHE_NAME],
    )
    upd_cache_data = await cache_update_finished.wait_call()
    assert upd_cache_data['arg']['restaurant_promos'] == expected_rest_promos
    assert upd_cache_data['arg']['retail_promos'] == []


async def test_adverts_cache_dump(taxi_eats_upsell):
    """
    Тест проверяет что кэш без ошибок дампится на диск и считывается обратно
    """
    await taxi_eats_upsell.write_cache_dumps(names=[CACHE_NAME])
    await taxi_eats_upsell.read_cache_dumps(names=[CACHE_NAME])


@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            '//testsuite/retail/EDACAT-1963-no-suitable-categories',
            'retail_promo',
            configs.YtTableType.Retail,
        ),
    ],
)
@pytest.mark.yt(static_table_data=['yt_promo_retail_EDACAT-1963.yaml'])
async def test_adverts_cache_retail_no_suitable_categories(
        taxi_eats_upsell, yt_apply, testpoint,
):
    """
    EDACAT-1963: проверяет, что данные нормально загружаются, если нет поля
    `suitable_categories` в таблице.
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    await taxi_eats_upsell.enable_testpoints()
    cache_data = await cache_update_finished.wait_call()
    assert cache_data['arg']['retail_promos'] == [
        {
            'promotion_name': 'retail_promo',
            'table_path': (
                'hahn.//testsuite/retail/EDACAT-1963-no-suitable-categories'
            ),
            'promo_places': [
                {
                    'place_id': 1,
                    'promo_items': [
                        {'public_id': '1', 'suitable_categories': []},
                        {'public_id': '2', 'suitable_categories': []},
                    ],
                },
                {
                    'place_id': 2,
                    'promo_items': [
                        {'public_id': '1', 'suitable_categories': []},
                        {'public_id': '2', 'suitable_categories': []},
                    ],
                },
                {
                    'place_id': 3,
                    'promo_items': [
                        {'public_id': '1', 'suitable_categories': []},
                        {'public_id': '3', 'suitable_categories': []},
                    ],
                },
            ],
        },
    ]


@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            '//home/eda/promo/retail1', 'promo1', configs.YtTableType.Retail,
        ),
        configs.YtTable(
            '//home/eda/promo/rest1',
            'promo2',
            configs.YtTableType.Restaurants,
        ),
    ],
)
@pytest.mark.yt(static_table_data=YT_DATA_TABLES)
async def test_adverts_cache_metrics(
        taxi_eats_upsell, yt_apply, testpoint, taxi_eats_upsell_monitor,
):
    """
    Проверяет запись кастомных метрик компонента adverts-cache
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    await taxi_eats_upsell.enable_testpoints()
    await cache_update_finished.wait_call()

    metrics = await taxi_eats_upsell_monitor.get_metric(CACHE_METRIC_NAME)
    assert metrics == {
        '$meta': {'solomon_children_labels': 'promo-type'},
        'restaurants': {
            '$meta': {'solomon_children_labels': 'promo-name'},
            'promo2': {
                'items_count': 2,
                'places_count': 2,
                'parsing_errors_count': 0,
            },
        },
        'retail': {
            '$meta': {'solomon_children_labels': 'promo-name'},
            'promo1': {
                'items_count': 3,
                'places_count': 2,
                'parsing_errors_count': 0,
            },
        },
    }


@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            '//home/eda/promo/rest-incremental1',
            'promo1',
            configs.YtTableType.Restaurants,
        ),
    ],
)
@pytest.mark.yt(static_table_data=['yt_promo_inc1.yaml'])
async def test_adverts_cache_metrics_incremental(
        taxi_eats_upsell,
        yt_apply,
        testpoint,
        taxi_eats_upsell_monitor,
        yt_client,
):
    """
    Проверяем, что метрики правильно обновляются при инкрементальном
    обновлении кэша
    """

    @testpoint(CACHE_UPDATE_FINISHED)
    def cache_update_finished(arg):
        pass

    await taxi_eats_upsell.enable_testpoints()
    await cache_update_finished.wait_call()

    expected_metrics = {
        '$meta': {'solomon_children_labels': 'promo-type'},
        'restaurants': {
            '$meta': {'solomon_children_labels': 'promo-name'},
            'promo1': {
                'items_count': 1,
                'places_count': 1,
                'parsing_errors_count': 0,
            },
        },
        'retail': {'$meta': {'solomon_children_labels': 'promo-name'}},
    }
    metrics = await taxi_eats_upsell_monitor.get_metric(CACHE_METRIC_NAME)
    assert metrics == expected_metrics

    # добавляем еще данных в таблицу и ждем инкрементального обновления
    brand_id = 100
    yt_client.write_table(
        '//home/eda/promo/rest-incremental1',
        [
            {'brand_id': brand_id, 'place_id': 1001, 'core_item_id': 2},
            {'brand_id': brand_id, 'place_id': 1002, 'core_item_id': 3},
        ],
    )
    expected_metrics['restaurants']['promo1']['items_count'] = 3
    expected_metrics['restaurants']['promo1']['places_count'] = 3

    await taxi_eats_upsell.invalidate_caches(
        clean_update=False, cache_names=[CACHE_NAME],
    )
    await cache_update_finished.wait_call()

    metrics = await taxi_eats_upsell_monitor.get_metric(CACHE_METRIC_NAME)
    assert metrics == expected_metrics
