from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

DEFAULT_REQUEST = {'slug': 'slug'}
CATEGORY_REQUEST = {**DEFAULT_REQUEST, 'category_uid': '1'}

EATER_ID = '12345'


@experiments.communications(categories_stories_enabled=True)
async def test_menu_goods_stories_config_disabled(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге отключено получение сториз на главной магазина, то запроса
    в eats-communications для главной магазина и категорий не будет,
    в ответе коммуникации отстутствуют
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    assert 'communications' not in response.json()['payload']
    assert 'communications' not in payload['categories'][0]


@experiments.communications(main_shop_stories_enabled=True)
async def test_menu_goods_stories_shop_main_page(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение сториз на главной магазина,
    то ответе будут сторизы из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )

    stories = [
        utils.make_communications_story('1'),
        utils.make_communications_story('2'),
    ]

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['stories']
        assert request.json['screen'] == 'shop_main_page'
        return {'payload': {'stories': stories, 'informers': []}}

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=DEFAULT_REQUEST,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    assert response.json()['payload']['communications'] == {
        'story': stories[0],
        'informers': [],
    }


@experiments.communications(main_shop_stories_enabled=True)
async def test_menu_goods_stories_categories_config_disabled(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение сториз только на главной магазина и в
    запросе есть категория, то при запроса в eats-communications для главной
    магазина и категорий не будет, в ответе коммуникации отсутствуют
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=CATEGORY_REQUEST,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    assert 'communications' not in response.json()['payload']
    assert 'communications' not in payload['categories'][0]


@experiments.communications(categories_stories_enabled=True)
async def test_menu_goods_stories_categories(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение сториз в категориях,
    то ответе в категориях будут сторизы из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    # категория с 1 сториз
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )
    # категория с 2 сториз
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory(
            'category_id_2', 'Фрукты', public_id=2, parent_id='1',
        ),
    )
    # категория без сториз
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory(
            'category_id_3', 'Фрукты', public_id=3, parent_id='1',
        ),
    )
    stories_1 = [utils.make_communications_story('1')]
    stories_2 = [
        utils.make_communications_story('2'),
        utils.make_communications_story('3'),
    ]

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['stories']
        assert request.json['screen'] == 'shop_category'
        assert request.json['categories'] == [
            {'category_id': '1'},
            {'category_id': '2'},
            {'category_id': '3'},
        ]
        return {
            'payload': [
                {
                    'category_id': '1',
                    'payload': {'stories': stories_1, 'informers': []},
                },
                {
                    'category_id': '2',
                    'payload': {'stories': stories_2, 'informers': []},
                },
            ],
        }

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=CATEGORY_REQUEST,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 3
    assert categories[0]['communications'] == {
        'story': stories_1[0],
        'informers': [],
    }
    assert categories[1]['communications'] == {
        'story': stories_2[0],
        'informers': [],
    }
    assert 'communications' not in categories[2]
