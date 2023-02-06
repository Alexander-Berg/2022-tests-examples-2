from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

DEFAULT_REQUEST = {'slug': 'slug'}
CATEGORY_REQUEST = {**DEFAULT_REQUEST, 'category_uid': '1'}


@experiments.communications(main_shop_informers_enabled=True)
async def test_menu_goods_informers_shop_main_page(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение информеров на главной магазина,
    то ответе будут информеры из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )

    informers = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['informers']
        assert request.json['screen'] == 'shop_main_page'
        return {'payload': {'stories': [], 'informers': informers}}

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=DEFAULT_REQUEST,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    assert response.json()['payload']['communications'] == {
        'informers': informers,
    }


@experiments.communications(main_shop_informers_enabled=True)
async def test_menu_goods_informers_categories_config_disabled(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение информеров только на главной магазина и в
    запросе menu/goods есть категория, то запроса в eats-communications не
    будет, в ответе коммуникации отсутствуют
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


@experiments.communications(categories_informers_enabled=True)
async def test_menu_goods_informers_categories(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение информеров в категориях,
    то ответе в категориях будут информеры из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    # категория с 1 информером
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )
    # категория с 2 информерами
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory(
            'category_id_2', 'Фрукты', public_id=2, parent_id='1',
        ),
    )
    # категория без информеров
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory(
            'category_id_3', 'Фрукты', public_id=3, parent_id='1',
        ),
    )

    informers_1 = [utils.make_text_image_informer('1')]
    informers_2 = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['informers']
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
                    'payload': {'stories': [], 'informers': informers_1},
                },
                {
                    'category_id': '2',
                    'payload': {'stories': [], 'informers': informers_2},
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
    assert categories[0]['communications'] == {'informers': informers_1}
    assert categories[1]['communications'] == {'informers': informers_2}
    assert 'communications' not in categories[2]
