from . import catalog
from . import colors
from . import experiments
from . import translations
from . import utils


YOU_ORDERED = 'Вы заказывали'
RECOMMENDS = 'Рекомендуем'

TRANSLATIONS = {
    'zero_suggest.ads': 'Реклама',
    'zero_suggest.you_ordered': YOU_ORDERED,
    'zero_suggest.recommends': RECOMMENDS,
}


YOU_ORDERED_COMPILATION = 'you_ordered'
RECOMMENDS_BRANDS = [4, 5, 6, 7]
DEFAULT_ADVERTS_LABEL = colors.ColoredText(
    text='_',
    text_key='zero_suggest.ads',
    color=[
        colors.Color(theme=colors.Theme.Light, color='#AAAAAA'),
        colors.Color(theme=colors.Theme.Dark, color='#FFFFFF'),
    ],
    background=[
        colors.Color(theme=colors.Theme.Light, color='#000000'),
        colors.Color(theme=colors.Theme.Dark, color='#111111'),
    ],
)

DEFAULT_FTS_COLORS = experiments.EatsFTSColors(
    adverts_label=DEFAULT_ADVERTS_LABEL,
)


@experiments.catalog_zero_suggest(
    blocks=[
        experiments.CatalogZeroSuggestBlock(
            title_key='zero_suggest.you_ordered',
            compilation_type=YOU_ORDERED_COMPILATION,
            limit=10,
        ),
        experiments.CatalogZeroSuggestBlock(
            title_key='zero_suggest.recommends',
            brand_ids=RECOMMENDS_BRANDS,
            limit=10,
        ),
    ],
)
@translations.eats_full_test_search_ru(TRANSLATIONS)
async def test_catalog_search_zero_suggest(
        taxi_eats_full_text_search, eats_catalog,
):
    """
    Проверяет нулевой экран поиска по каталогу
    """

    request_params = {
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'delivery',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
    }

    you_ordered_place = catalog.Place(
        id=1, slug='slug_1', brand=catalog.Brand(id=1),
    )

    recommends_place = catalog.Place(
        id=5, slug='slug_5', brand=catalog.Brand(id=5),
    )

    another_recommends_place = catalog.Place(
        id=7, slug='slug_7', brand=catalog.Brand(id=7),
    )

    eats_catalog.add_block(
        catalog.Block(id='block_0', list=[you_ordered_place]),
    )

    eats_catalog.add_block(
        catalog.Block(
            id='block_1', list=[recommends_place, another_recommends_place],
        ),
    )

    def catalog_assert(request):
        data = request.json

        for field in ('latitude', 'longitude'):
            assert data[field] == request_params['location'][field]
        for field in ('region_id', 'shipping_type'):
            assert data[field] == request_params[field]

        blocks = data['blocks']
        assert len(blocks) == 2

        assert blocks[0] == {
            'id': 'block_0',
            'type': 'open',
            'low': 0,
            'min_count': 0,
            'no_data': False,
            'compilation_type': YOU_ORDERED_COMPILATION,
            'limit': 10,
        }

        # Сравниваем предикат отдельно, потому что в нем сет, порядок элементов
        # в котором не детерменирован
        block_condition = blocks[1].pop('condition')
        assert block_condition['type'] == 'in_set'
        assert block_condition['init']['arg_name'] == 'brand_id'
        assert block_condition['init']['set_elem_type'] == 'int'
        assert frozenset(block_condition['init']['set']) == frozenset(
            RECOMMENDS_BRANDS,
        )

        assert blocks[1] == {
            'id': 'block_1',
            'type': 'open',
            'low': 0,
            'min_count': 0,
            'no_data': False,
            'limit': 10,
        }

    eats_catalog.assert_callback = catalog_assert

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called == 1
    assert response.status == 200

    data = response.json()
    assert len(data['blocks']) == 2

    you_ordered_block = data['blocks'][0]

    assert you_ordered_block['title'] == YOU_ORDERED
    assert you_ordered_block['type'] == 'places'
    utils.assert_has_catalog_place(
        you_ordered_block['payload'], you_ordered_place,
    )

    recommends_block = data['blocks'][1]
    assert recommends_block['title'] == RECOMMENDS
    assert recommends_block['type'] == 'places'
    utils.assert_has_catalog_place(
        recommends_block['payload'], recommends_place,
    )
    utils.assert_has_catalog_place(
        recommends_block['payload'], another_recommends_place,
    )


@experiments.catalog_zero_suggest(
    blocks=[
        experiments.CatalogZeroSuggestBlock(
            title_key='testsuite',
            advert_settings=experiments.ZeroSuggestBlockAdvertSettings(
                limit=3,
                yabs_parameters=experiments.ZeroSuggestBlockYabsParams(
                    page_id=1, target_ref='testsuite', page_ref='testsuite',
                ),
            ),
        ),
    ],
)
@experiments.eats_fts_colors(DEFAULT_FTS_COLORS)
@translations.eats_full_test_search_ru(TRANSLATIONS)
async def test_catalog_search_zero_suggest_with_ads(
        taxi_eats_full_text_search, eats_catalog,
):
    """
    EDACAT-2558: проверяет, что в блоке нулевого поиска есть реклама.
    """

    common_place = catalog.Place(
        id=1, slug='slug_1', brand=catalog.Brand(id=1),
    )
    eats_catalog.add_block(catalog.Block(id='block_0', list=[common_place]))

    advert_place = catalog.Place(
        id=2,
        slug='slug_2',
        brand=catalog.Brand(id=2),
        advertisement=catalog.Advertisement(
            view_url='eda.yandex.ru/slug_2/view',
            click_url='eda.yandex.ru/slug_2/click',
        ),
    )

    eats_catalog.add_block(
        catalog.Block(id='block_0_advert', list=[advert_place]),
    )

    def catalog_assert(request):
        data = request.json
        assert 'blocks' in data

        blocks = data['blocks']
        assert len(blocks) == 2
        assert blocks[0] == {
            'id': 'block_0',
            'type': 'open',
            'low': 0,
            'min_count': 0,
            'no_data': False,
        }
        assert blocks[1] == {
            'id': 'block_0_advert',
            'type': 'open',
            'low': 0,
            'min_count': 0,
            'no_data': False,
            'limit': 3,
            'advert_settings': {
                'yabs_parameters': {
                    'page_id': 1,
                    'target_ref': 'testsuite',
                    'page_ref': 'testsuite',
                },
            },
        }

    eats_catalog.assert_callback = catalog_assert

    request_params = {
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'delivery',
        'delivery_time': {'time': '2022-03-14T14:00:00+00:00', 'zone': 3},
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called == 1
    assert response.status == 200

    data = response.json()
    assert len(data['blocks']) == 1

    block = data['blocks'].pop(0)
    assert block['type'] == 'places'

    places = block['payload']
    assert len(places) == 2
    assert places[0]['slug'] == advert_place.slug
    assert places[1]['slug'] == common_place.slug

    assert 'advertisements' in places[0]
    advertisements = places[0]['advertisements']
    print(advertisements)
    assert advertisements['view_url'] == advert_place.advertisement.view_url
    assert advertisements['click_url'] == advert_place.advertisement.click_url
    assert advertisements['label'] == DEFAULT_ADVERTS_LABEL.as_layout_model(
        TRANSLATIONS,
    )


@experiments.catalog_zero_suggest(
    blocks=[
        experiments.CatalogZeroSuggestBlock(title_key='testsuite_1'),
        experiments.CatalogZeroSuggestBlock(title_key='testsuite_2'),
    ],
)
async def test_catalog_search_zero_suggest_no_fail_with_less_blocks(
        taxi_eats_full_text_search, eats_catalog,
):
    """
    EDACAT-2593: проверяет, что в код не коркается, когда каталог вернул
    меньше блоков, чем запрашивалось.
    """

    place = catalog.Place(id=1, slug='slug_1', brand=catalog.Brand(id=1))
    eats_catalog.add_block(catalog.Block(id='block_0', list=[place]))

    def catalog_assert(request):
        data = request.json
        assert 'blocks' in data

        blocks = data['blocks']
        assert len(blocks) == 2

    eats_catalog.assert_callback = catalog_assert

    request_params = {
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'delivery',
        'delivery_time': {'time': '2022-03-14T14:00:00+00:00', 'zone': 3},
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called == 1
    assert response.status == 200

    data = response.json()
    assert len(data['blocks']) == 1

    block = data['blocks'].pop(0)
    assert block['type'] == 'places'

    places = block['payload']
    assert len(places) == 1
    assert places[0]['slug'] == place.slug


@experiments.catalog_zero_suggest(
    blocks=[
        experiments.CatalogZeroSuggestBlock(
            title_key='zero_suggest.you_ordered',
            compilation_type=YOU_ORDERED_COMPILATION,
            limit=10,
        ),
        experiments.CatalogZeroSuggestBlock(
            title_key='zero_suggest.recommends',
            brand_ids=RECOMMENDS_BRANDS,
            limit=10,
            advert_settings=experiments.ZeroSuggestBlockAdvertSettings(
                limit=1,
                yabs_parameters=experiments.ZeroSuggestBlockYabsParams(
                    page_id=1, target_ref='testsuite', page_ref='testsuite',
                ),
            ),
        ),
    ],
)
@experiments.eats_fts_colors(DEFAULT_FTS_COLORS)
@translations.eats_full_test_search_ru(TRANSLATIONS)
async def test_catalog_search_zero_suggest_fix_use_after_move(
        taxi_eats_full_text_search, eats_catalog,
):
    """
    EDACAT-2558: проверяет, что исправлен use-after-move.
    """

    places = []
    for place_id in range(1, 11):
        places.append(
            catalog.Place(
                id=place_id,
                slug=f'slug_{place_id}',
                brand=catalog.Brand(id=place_id),
            ),
        )

    eats_catalog.add_block(catalog.Block(id='block_0', list=places))
    eats_catalog.add_block(catalog.Block(id='block_1', list=places))

    advert_place = catalog.Place(
        id=30,
        slug='slug_30',
        brand=catalog.Brand(id=30),
        advertisement=catalog.Advertisement(
            view_url='eda.yandex.ru/slug_30/view',
            click_url='eda.yandex.ru/slug_30/click',
        ),
    )

    eats_catalog.add_block(
        catalog.Block(id='block_1_advert', list=[advert_place]),
    )

    request_params = {
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'delivery',
        'delivery_time': {'time': '2022-03-14T14:00:00+00:00', 'zone': 3},
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called == 1
    assert response.status == 200

    data = response.json()
    assert len(data['blocks']) == 2

    block = data['blocks'].pop(0)
    assert block['type'] == 'places'
    assert block['title'] == YOU_ORDERED
    places = block['payload']
    assert len(places) == 10

    block = data['blocks'].pop(0)
    assert block['type'] == 'places'
    assert block['title'] == RECOMMENDS

    places = block['payload']
    assert len(places) == 11
    assert places[0]['slug'] == advert_place.slug

    assert 'advertisements' in places[0]
    advertisements = places[0]['advertisements']
    assert advertisements['view_url'] == advert_place.advertisement.view_url
    assert advertisements['click_url'] == advert_place.advertisement.click_url
    assert advertisements['label'] == DEFAULT_ADVERTS_LABEL.as_layout_model(
        TRANSLATIONS,
    )
