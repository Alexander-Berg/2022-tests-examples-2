import pytest

from tests_eats_restaurant_menu import util


@pytest.mark.parametrize(
    'available_sort',
    [
        pytest.param(True, id='available_sort_on'),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_RESTAURANT_MENU_SORT_CATEGORIES_BY_AVAILABLE=False,
            ),
            id='available_sort_off',
        ),
    ],
)
@util.get_sort_exp3_with_value('as_is')
async def test_simple_menu_modifier(taxi_eats_restaurant_menu, available_sort):
    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=4, available=False, items=[util.build_item(1)],
                ),
                util.build_category(
                    category_id=5, available=True, items=[util.build_item(2)],
                ),
                util.build_category(
                    category_id=7, available=False, items=[util.build_item(3)],
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
    if available_sort:
        actual_order = []
        for category in response.json()['payload']['categories']:
            actual_order.append(category.get('id'))
        assert actual_order == [5, 4, 7]
    else:
        assert request == response.json()
