import pytest

from tests_eats_restaurant_menu import util


def qsr_pickup_user(personal_phone_id):
    return pytest.mark.experiments3(
        name='open_qsr_pickup',
        consumers=['eats_restaurant_menu'],
        clauses=[
            {
                'title': 'courier',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'personal_phone_id',
                        'arg_type': 'string',
                        'value': personal_phone_id,
                    },
                },
            },
            {
                'title': 'default',
                'value': {'enabled': False},
                'predicate': {'type': 'true', 'init': {}},
            },
        ],
    )


def menu_disabled_categories(category_names):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_menu_disabled_categories',
        consumers=['eats_restaurant_menu'],
        clauses=[
            {
                'value': {'category_names': category_names},
                'predicate': {'type': 'true'},
            },
        ],
    )


COURIER_ID = '123'
NON_COURIER_ID = '456'
DISABLED_CATEGORIES = ['category1', 'category2']


@pytest.mark.parametrize(
    'personal_phone_id',
    [
        pytest.param(COURIER_ID, id='courier'),
        pytest.param(NON_COURIER_ID, id='ordinary_person'),
    ],
)
@pytest.mark.parametrize(
    'disabled_categories',
    [
        pytest.param(
            [],
            marks=menu_disabled_categories([]),
            id='no_disabled_categories',
        ),
        pytest.param(
            DISABLED_CATEGORIES,
            marks=menu_disabled_categories(DISABLED_CATEGORIES),
            id='some_categories_are_disabled',
        ),
    ],
)
@util.get_sort_exp3_with_value('as_is')
@qsr_pickup_user(COURIER_ID)
async def test_hide_category_sorter(
        taxi_eats_restaurant_menu, personal_phone_id, disabled_categories,
):
    categories = [
        util.build_category(
            category_id=4,
            available=False,
            name='category1',
            items=[util.build_item(1)],
        ),
        util.build_category(
            category_id=5,
            available=True,
            name='category1',
            items=[util.build_item(2)],
        ),
        util.build_category(
            category_id=7, available=False, items=[util.build_item(3)],
        ),
        util.build_category(
            category_id=8,
            available=True,
            name='category2',
            items=[util.build_item(4)],
        ),
        util.build_category(
            category_id=9,
            available=True,
            name='category3',
            items=[util.build_item(2)],
        ),
    ]
    category_ids = {cat.get('id'): cat.get('name') for cat in categories}
    request = {'slug': 'test_slug', 'payload': {'categories': categories}}

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={
            'X-Eats-User': (
                f'user_id=21, personal_phone_id={personal_phone_id}'
            ),
        },
    )
    assert response.status_code == 200
    response_json = response.json()

    for cat in response_json['payload']['categories']:
        assert cat.get('id') in category_ids
        del category_ids[cat.get('id')]

        if personal_phone_id == NON_COURIER_ID:
            assert 'name' not in cat or cat['name'] not in disabled_categories

    if personal_phone_id == COURIER_ID:
        assert not category_ids
    else:
        assert all(
            name in disabled_categories for _, name in category_ids.items()
        )


@pytest.mark.parametrize(
    'personal_phone_id, expected_order',
    [
        pytest.param(COURIER_ID, [5, 8, 10, 4, 7, 9], id='courier'),
        pytest.param(NON_COURIER_ID, [8, 10, 7, 9], id='ordinary_person'),
    ],
)
@util.get_sort_exp3_with_value('as_is')
@qsr_pickup_user(COURIER_ID)
@menu_disabled_categories(DISABLED_CATEGORIES)
async def test_hiding_categories_preserves_order(
        taxi_eats_restaurant_menu, personal_phone_id, expected_order,
):
    categories = [
        util.build_category(
            category_id=4,
            available=False,
            name='category1',
            items=[util.build_item(1)],
        ),
        util.build_category(
            category_id=5,
            available=True,
            name='category2',
            items=[util.build_item(2)],
        ),
        util.build_category(
            category_id=7, available=False, items=[util.build_item(3)],
        ),
        util.build_category(
            category_id=8,
            available=True,
            name='category4',
            items=[util.build_item(4)],
        ),
        util.build_category(
            category_id=9,
            available=False,
            name='category4',
            items=[util.build_item(2)],
        ),
        util.build_category(
            category_id=10,
            available=True,
            name='category5',
            items=[util.build_item(5)],
        ),
    ]
    request = {'slug': 'test_slug', 'payload': {'categories': categories}}

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={
            'X-Eats-User': (
                f'user_id=21, personal_phone_id={personal_phone_id}'
            ),
        },
    )
    assert response.status_code == 200
    response_json = response.json()

    assert [
        cat.get('id') for cat in response_json['payload']['categories']
    ] == expected_order
