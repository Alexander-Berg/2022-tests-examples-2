import pytest

from . import configs
from . import eats_catalog_storage
from . import eats_products
from . import eats_rest_menu_storage as rest_menu_storage
from . import experiments
from . import umlaas_eats
from . import utils


PLACE_ID: int = 1


@experiments.promo_settings(positions=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
@pytest.mark.yt(
    static_table_data=[
        'yt_test_promo_experiments_table_1.yaml',
        'yt_test_promo_experiments_table_2.yaml',
        'yt_test_promo_experiments_table_3.yaml',
        'yt_test_promo_experiments_table_4.yaml',
        'yt_test_promo_experiments_table_5.yaml',
    ],
)
@pytest.mark.parametrize(
    'item_ids, expected_ids',
    [
        pytest.param(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_1',
                            promotion='testsuite',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite'),
            ),
            id='single promo experiment for all consumers',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_1',
                            promotion='testsuite',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion(
                    'testsuite', consumers=[experiments.CONSUMER_PROMOTER],
                ),
            ),
            id='single promo experiment for deprecated consumer',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_1',
                            promotion='testsuite',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion(
                    'testsuite', consumers=[experiments.CONSUMER_UPSELL],
                ),
            ),
            id='single promo experiment for new consumer',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_3',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2', priority=100),
                experiments.create_promotion('testsuite_3', priority=50),
            ),
            id='two promo experiments',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            [4, 5, 1, 2, 3],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_3',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2', priority=50),
                experiments.create_promotion('testsuite_3', priority=100),
            ),
            id='two promo experiments sorted by priority',
        ),
        pytest.param(
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 8, 9, 6, 7, 1, 2, 3],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_3',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_4',
                            promotion='testsuite_4',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_5',
                            promotion='testsuite_5',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2', priority=10),
                experiments.create_promotion('testsuite_3', priority=100),
                experiments.create_promotion('testsuite_4', priority=50),
                experiments.create_promotion('testsuite_5', priority=90),
            ),
            id='four non-sorted promo experiments',
        ),
        pytest.param(
            [1, 2, 3, 4, 5, 6, 7],
            [1, 2, 3, 6, 7, 4, 5],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_3',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_4',
                            promotion='testsuite_4',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_5',
                            promotion='testsuite_5',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2', priority=10),
                experiments.create_promotion('testsuite_3', priority=50),
                experiments.create_promotion('testsuite_4', priority=70),
                experiments.create_promotion('testsuite_2', priority=100),
            ),
            id='same experiment with different priority',
        ),
        pytest.param(
            [1, 2, 3, 4, 5, 6, 7],
            [4, 5, 1, 2, 3, 6, 7],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_3',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_4',
                            promotion='testsuite_4',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2', priority=50),
                experiments.create_promotion('testsuite_3', priority=100),
                experiments.create_promotion('testsuite_4'),
            ),
            id='exp with no priority moved to the end',
        ),
        pytest.param(
            [1, 2, 3],
            [1, 2, 3],
            marks=(
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//testsuite/test_promo_experiments/table_2',
                            promotion='testsuite_3',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
                experiments.create_promotion('testsuite_2'),
                experiments.create_promotion('testsuite_3'),
            ),
            id='only unique items in response',
        ),
    ],
)
async def test_promo_experiments(
        taxi_eats_upsell,
        yt_apply,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        item_ids,
        expected_ids,
):
    """
    EDACAT-1425: Проверяет, что для коммерческих рекомендаций используется
    массив экспериментов. Также проверяет, что в ответе будут только уникальные
    рестораны.
    """

    for item_id in item_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=PLACE_ID),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
            },
        },
    )
    assert response.status_code == 200
    assert core_menu_items.times_called == 2
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1

    items = response.json()['payload']['items']
    assert len(expected_ids) == len(items)
    for expected_id, item in zip(expected_ids, items):
        assert expected_id == item['id']
        assert 'promoted' in item


@experiments.promo_settings(positions=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
@pytest.mark.parametrize(
    'business, item_ids, expected_ids',
    [
        pytest.param(
            eats_catalog_storage.Business.RESTAURANT,
            [1, 2, 3],
            [1, 2, 3],
            marks=(
                experiments.create_promo_experiment(
                    'single', {'promo_name': 'promo'},
                ),
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//home/eda/promo/rest1',
                            promotion='promo',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
            ),
            id='single rest promo',
        ),
        pytest.param(
            eats_catalog_storage.Business.RESTAURANT,
            [1, 2, 3, 4],
            [4, 1, 2, 3],
            marks=(
                experiments.create_promo_experiment(
                    'one', {'promo_name': 'promo_1'},
                ),
                experiments.create_promo_experiment(
                    'two', {'promo_name': 'promo_2'},
                ),
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//home/eda/promo/rest1',
                            promotion='promo_1',
                            type=configs.YtTableType.Restaurants,
                        ),
                        configs.YtTable(
                            path='//home/eda/promo/rest2',
                            promotion='promo_2',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
            ),
            id='2 rest promos',
        ),
        pytest.param(
            eats_catalog_storage.Business.RESTAURANT,
            [1, 2, 3],
            [1, 2, 3],
            marks=(
                experiments.create_promo_experiment(
                    'single',
                    {
                        'promo_name': 'promo',
                        'places': [
                            {
                                'place_id': PLACE_ID,
                                'items': [{'item_id': 4}, {'item_id': 5}],
                            },
                        ],
                    },
                ),
                configs.adverts_cache_config(
                    tables=[
                        configs.YtTable(
                            path='//home/eda/promo/rest1',
                            promotion='promo',
                            type=configs.YtTableType.Restaurants,
                        ),
                    ],
                ),
            ),
            id='promo with exp items (ignored)',
        ),
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_promo_rest1.yaml',
        'yt_promo_rest2.yaml',
        'yt_promo_retail1.yaml',
    ],
)
async def test_promo_cached_data(
        taxi_eats_upsell,
        yt_apply,
        eats_catalog_storage_service,
        products_id_mappings,
        products_menu_items,
        core_menu_items,
        umlaas_suggest,
        business,
        item_ids,
        expected_ids,
):
    """
    Проверяет, что если в промо эксперименте указано имя промо компании,
    то данные будут браться из кэшированных YT таблиц,
    пути к которым указаны в конфиге
    """

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(
            place_id=PLACE_ID, business=business,
        ),
    )
    for item_id in item_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))
        products_menu_items.add_item(
            eats_products.RetailItem(
                core_item_id=item_id, public_id=str(item_id),
            ),
        )
        products_id_mappings.add_mapping(eats_products.Mapping(item_id))

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
            },
        },
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1

    if business == eats_catalog_storage.Business.RESTAURANT:
        assert core_menu_items.times_called == 2
        assert products_menu_items.times_called == 0
    else:
        assert core_menu_items.times_called == 1
        assert products_menu_items.times_called == 1

    items = response.json()['payload']['items']
    assert len(expected_ids) == len(items)
    for expected_id, item in zip(expected_ids, items):
        assert expected_id == item['id']
        assert 'promoted' in item


@pytest.mark.parametrize(
    'called_retail',
    [
        pytest.param(
            1,
            marks=(experiments.upsell_retail_switcher(True)),
            id='enabled exp - enabled retail',
        ),
        pytest.param(
            0,
            marks=(experiments.upsell_retail_switcher(False)),
            id='disabled exp - disabled retail',
        ),
        pytest.param(1, id='no exp - enabled retail'),
    ],
)
async def test_upsell_retail_switcher(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        products_id_mappings,
        products_menu_items,
        umlaas_eats_retail_suggest,
        called_retail,
):
    """
    Проверяет выключается ли ретейл по эксперименту
    """
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(
            place_id=PLACE_ID, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    umlaas_eats_retail_suggest.set_recommendations(['2', '3'])
    item_ids = [1, 2, 3]

    for item_id in item_ids:
        products_menu_items.add_item(
            eats_products.RetailItem(
                core_item_id=item_id, public_id=str(item_id),
            ),
        )
        products_id_mappings.add_mapping(eats_products.Mapping(item_id))

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
                'place_slug': f'place_{PLACE_ID}',
            },
        },
    )

    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert products_menu_items.times_called == 1
    assert umlaas_eats_retail_suggest.times_called == called_retail


async def test_upsell_no_common_flow_in_retail(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        products_id_mappings,
        products_menu_items,
        umlaas_eats_retail_suggest,
        core_menu_items,
):
    """
    Проверяет, что запрос для ритейла идёт не в common flow
    """

    item_ids = [1, 2, 3]
    expected_ids = [2, 3]

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(
            place_id=PLACE_ID, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    for item_id in item_ids:
        products_menu_items.add_item(
            eats_products.RetailItem(
                core_item_id=item_id, public_id=str(item_id),
            ),
        )
        products_id_mappings.add_mapping(eats_products.Mapping(item_id))

    umlaas_eats_retail_suggest.set_recommendations(['2', '3'])

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
                'place_slug': f'place_{PLACE_ID}',
            },
        },
    )

    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_eats_retail_suggest.times_called == 1

    assert core_menu_items.times_called == 0
    assert products_menu_items.times_called == 1

    items = response.json()['payload']['items']
    assert len(expected_ids) == len(items)
    for expected_id, item in zip(expected_ids, items):
        assert expected_id == item['id']


@experiments.create_rest_menu_storage_exp()
@experiments.promo_settings(positions=[0, 1, 2, 3, 4])
@pytest.mark.yt(static_table_data=['yt_test_promo_experiments_table_1.yaml'])
@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            path='//testsuite/test_promo_experiments/table_1',
            promotion='testsuite',
            type=configs.YtTableType.Restaurants,
        ),
    ],
)
@experiments.create_promotion('testsuite')
async def test_upsell_new_candidates_from_erms(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        rest_menu_storage_get_items,
        core_menu_items,
        umlaas_suggest,
        mockserver,
):
    """
    EDACAT-2793: используем новый способ получения кандидатов (через erms)
    """

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def discounts(request):
        return {}

    item1 = rest_menu_storage.Item(
        id='item_id_1',
        origin_id='original',
        name='first_item',
        adult=True,
        legacy_id=1,
        categories_ids=[rest_menu_storage.CategoryIds(id='2', legacy_id=2)],
        price='10',
    )

    item2 = rest_menu_storage.Item(
        id='item_id_1',
        origin_id='original',
        name='first_item',
        adult=True,
        legacy_id=2,
        categories_ids=[rest_menu_storage.CategoryIds(id='2', legacy_id=2)],
        price='10',
    )

    item3 = rest_menu_storage.Item(
        id='item_id_1',
        origin_id='original',
        name='first_item',
        adult=True,
        legacy_id=3,
        categories_ids=[rest_menu_storage.CategoryIds(id='2', legacy_id=2)],
        price='10',
    )

    expected_ids = [1, 2, 3]

    for item_id in expected_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))

    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(place_id='1', items=[item1, item2, item3]),
    ]

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=PLACE_ID),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
            },
        },
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1
    assert discounts.times_called > 0

    items = response.json()['payload']['items']
    assert len(expected_ids) == len(items)
    for expected_id, item in zip(expected_ids, items):
        assert expected_id == item['id']
        assert 'promoted' in item


@experiments.promo_settings(positions=[0, 1, 2, 3, 4])
@pytest.mark.yt(static_table_data=['yt_test_promo_experiments_table_1.yaml'])
@experiments.upsell_sources([experiments.SourceType.ADVERT])
@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            path='//testsuite/test_promo_experiments/table_1',
            promotion='testsuite',
            type=configs.YtTableType.Restaurants,
        ),
    ],
)
@experiments.disable_adverts()
@experiments.create_promotion('testsuite')
@pytest.mark.parametrize(
    'expected_ids, core_calls', [pytest.param([2, 3], 2, id='old flow')],
)
async def test_upsell_advertisement_disabled_v1_upsell(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        expected_ids,
        core_calls,
):
    """
    Проверяем, что после удаления экспа, отключающий рекламу, все также работает
    """

    item_ids = [1, 2, 3, 4, 5]

    umlaas_suggest.add_items(
        [umlaas_eats.SuggestItem(uuid='2'), umlaas_eats.SuggestItem(uuid='3')],
    )

    for item_id in item_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=PLACE_ID),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {},
            },
        },
    )
    assert response.status_code == 200
    assert core_menu_items.times_called == core_calls
    assert eats_catalog_storage_service.times_called == 1

    items = response.json()['payload']['items']
    assert len(items) == len(expected_ids)
    for item, item_id in zip(items, expected_ids):
        assert item['id'] == item_id
