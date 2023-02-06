import pytest

from tests_eats_restaurant_menu import util


@pytest.mark.parametrize(
    'expected_sort',
    [
        pytest.param(
            'popularity',
            marks=[
                util.get_sort_exp3_with_value('popularity'),
                pytest.mark.pgsql('eats_misc', files=['popularity_items.sql']),
            ],
            id='popularity',
        ),
        pytest.param(
            'promotions',
            marks=util.get_sort_exp3_with_value('promotions'),
            id='promotions',
        ),
        pytest.param(
            'order_history',
            marks=[
                util.get_sort_exp3_with_value('order_history'),
                pytest.mark.pgsql(
                    'eats_misc', files=['order_history_popularity_items.sql'],
                ),
            ],
            id='order_history',
        ),
        pytest.param(
            'as_is', marks=util.get_sort_exp3_with_value('as_is'), id='as_is',
        ),
        pytest.param('as_is', id='no_exp'),
    ],
)
async def test_simple_menu_modifier(
        taxi_eats_restaurant_menu, expected_sort, mockserver, load_json,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eats_ordershistory(request):
        return load_json('ordershistory_get_orders_response.json')

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=4,
                    available=True,
                    items=[
                        util.build_item(
                            3,
                            picture={'uri': 'b', 'ratio': 1.0},
                            available=False,
                        ),
                        util.build_item(1, picture={'uri': 'b', 'ratio': 1.0}),
                        util.build_item(4),
                        util.build_item(
                            2,
                            promo_types=[
                                {
                                    'id': 1,
                                    'name': 'promo_name',
                                    'pictureUri': '/images/1370147.png',
                                    'detailedPictureUrl': (
                                        '/images/1370147.png'
                                    ),
                                },
                            ],
                        ),
                    ],
                ),
                util.build_category(
                    category_id=5,
                    available=True,
                    items=[
                        util.build_item(2),
                        util.build_item(4, picture={'uri': 'b', 'ratio': 1.0}),
                        util.build_item(
                            6,
                            picture={'uri': 'b', 'ratio': 1.0},
                            promo_types=[
                                {
                                    'id': 1,
                                    'name': 'promo_name',
                                    'pictureUri': '/images/1370147.png',
                                    'detailedPictureUrl': (
                                        '/images/1370147.png'
                                    ),
                                },
                            ],
                        ),
                        util.build_item(
                            8,
                            picture={'uri': 'b', 'ratio': 1.0},
                            promo_types=[
                                {
                                    'id': 1,
                                    'name': 'promo_name',
                                    'pictureUri': '/images/1370147.png',
                                    'detailedPictureUrl': (
                                        '/images/1370147.png'
                                    ),
                                },
                            ],
                            available=False,
                        ),
                        util.build_item(5),
                        util.build_item(7),
                        util.build_item(
                            10,
                            promo_types=[
                                {
                                    'id': 1,
                                    'name': 'promo_name',
                                    'pictureUri': '/images/1370147.png',
                                    'detailedPictureUrl': (
                                        '/images/1370147.png'
                                    ),
                                },
                            ],
                            available=False,
                        ),
                        util.build_item(
                            3,
                            promo_types=[
                                {
                                    'id': 1,
                                    'name': 'promo_name',
                                    'pictureUri': '/images/1370147.png',
                                    'detailedPictureUrl': (
                                        '/images/1370147.png'
                                    ),
                                },
                            ],
                        ),
                    ],
                ),
                util.build_category(
                    category_id=7,
                    available=True,
                    items=[
                        util.build_item(20),
                        util.build_item(
                            40, picture={'uri': 'b', 'ratio': 1.0},
                        ),
                    ],
                ),
            ],
        },
    }
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200
    del request['slug']

    response_categories = response.json()['payload']['categories']
    if expected_sort == 'as_is':
        assert request == response.json()
    elif expected_sort == 'order_history':
        expected_items_order = {
            4: [4, 1, 2, 3],
            5: [3, 4, 2, 6, 7, 5, 10, 8],
            7: [40, 20],
        }
        util.compare_order(expected_items_order, response_categories)
    elif expected_sort == 'popularity':
        expected_items_order = {
            4: [1, 4, 2, 3],
            5: [6, 4, 5, 3, 2, 7, 8, 10],
            7: [40, 20],
        }
        util.compare_order(expected_items_order, response_categories)
    elif expected_sort == 'promotions':
        expected_items_order = {
            4: [1, 2, 4, 3],
            5: [6, 4, 3, 2, 5, 7, 8, 10],
            7: [40, 20],
        }
        util.compare_order(expected_items_order, response_categories)
    else:
        assert False, f'sort_type {expected_sort} is unsupported'
