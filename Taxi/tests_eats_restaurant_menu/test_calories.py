import pytest

from tests_eats_restaurant_menu import config
from tests_eats_restaurant_menu import util


@config.eats_restaurant_menu(max_item_kilocalories='800')
@pytest.mark.parametrize(
    'measure,kilocalories,expected',
    (
        pytest.param(
            {'value': '100', 'measure_unit': 'g'}, '200', '200', id='200kkal',
        ),
        pytest.param(
            {'value': '1', 'measure_unit': 'kg'}, '200', '2000', id='from_kg',
        ),
        pytest.param(
            {'value': '100', 'measure_unit': 'g'}, '850', None, id='filtered',
        ),
    ),
)
async def test_calories(
        taxi_eats_restaurant_menu, measure, kilocalories, expected,
):
    nutrients = {
        'calories': {'value': kilocalories, 'unit': 'kkal'},
        'fats': {'value': '1', 'unit': ''},
        'proteins': {'value': '1', 'unit': ''},
        'carbohydrates': {'value': '1', 'unit': ''},
    }

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[
                        util.build_item(
                            1, measure=measure, nutrients=nutrients,
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
    item = response.json()['payload']['categories'][0]['items'][0]
    if expected:
        assert item['nutrients']['calories']['value'] == expected
    else:
        assert 'nutrients' not in item
