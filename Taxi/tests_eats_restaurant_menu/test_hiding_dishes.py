import pytest

from tests_eats_restaurant_menu import util


def get_hiding_exp3_with_value(hiding_type: str):
    return pytest.mark.experiments3(
        name='eats_restaurant_menu_hiding_dishes_in_stop_list',
        consumers=['eats_restaurant_menu'],
        is_config=False,
        default_value={'hiding_type': hiding_type},
    )


@util.get_sort_exp3_with_value('as_is')
@pytest.mark.parametrize(
    'expected_hiding',
    [
        pytest.param(
            'hiding_dishes_in_stop_list',
            marks=get_hiding_exp3_with_value('hiding_dishes_in_stop_list'),
            id='hiding_dishes_in_stop_list',
        ),
        pytest.param(
            'as_is', marks=get_hiding_exp3_with_value('as_is'), id='as_is',
        ),
        pytest.param('as_is', id='no_exp'),
    ],
)
async def test_simple_menu_hiding(taxi_eats_restaurant_menu, expected_hiding):
    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=None,
                    available=True,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(1),
                        util.build_item(4),
                    ],
                ),
                util.build_category(
                    category_id=7,
                    available=True,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(1),
                        util.build_item(4),
                    ],
                ),
                util.build_category(
                    category_id=4,
                    available=False,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(1),
                        util.build_item(4),
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

    if expected_hiding == 'hiding_dishes_in_stop_list':
        expected_items_order = {None: [3, 1, 4], 7: [1, 4], 4: [3, 1, 4]}
        util.compare_order(
            expected_items_order, response.json()['payload']['categories'],
        )
    else:
        assert request == response.json()


@util.get_sort_exp3_with_value('as_is')
@get_hiding_exp3_with_value('hiding_dishes_in_stop_list')
async def test_empty_categories(taxi_eats_restaurant_menu, load_json):
    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=None,
                    available=True,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(1),
                    ],
                ),
                util.build_category(
                    category_id=7,
                    available=True,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(1, available=False),
                    ],
                ),
                util.build_category(
                    category_id=4,
                    available=False,
                    items=[
                        util.build_item(3, available=False),
                        util.build_item(4),
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

    expected_categories = set([None, 4])
    actual_categories = {
        category.get('id')
        for category in response.json()['payload']['categories']
    }

    assert actual_categories == expected_categories
