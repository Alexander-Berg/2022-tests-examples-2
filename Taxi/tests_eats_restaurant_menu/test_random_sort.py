import datetime
import typing as tp

import pytest

from tests_eats_restaurant_menu import util


def get_request_body(categories: tp.Dict[tp.Optional[int], tp.List[int]]):
    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=key,
                    available=True,
                    items=[
                        util.build_item(
                            item_id=item_id, price=10.5, available=True,
                        )
                        for item_id in values
                    ],
                )
                for key, values in categories.items()
            ],
        },
    }
    return request


@util.get_sort_exp3_with_value('random')
@pytest.mark.parametrize(
    'user_id,input_categories,expected_categories',
    [
        pytest.param(
            'device1',
            {1: [1, 2, 3, 4, 5]},
            {1: [2, 5, 1, 3, 4]},
            id='single_category',
        ),
        pytest.param('device1', {1: [1]}, {1: [1]}, id='single_item'),
        pytest.param(
            'device2',
            {1: [1, 2, 3, 4], 2: [8, 7, 6, 5]},
            {1: [3, 2, 1, 4], 2: [5, 7, 6, 8]},
            id='multiple_categories',
        ),
        pytest.param(
            'device2',
            {1: [1, 2, 3, 4], None: [8, 7, 6, 5]},
            {1: [3, 2, 1, 4], None: [8, 7, 6, 5]},
            id='null_category',
        ),
    ],
)
@pytest.mark.now('2020-01-01T12:00:00+0000')
async def test_random_sort(
        taxi_eats_restaurant_menu,
        user_id,
        input_categories,
        expected_categories,
):
    request_body = get_request_body(input_categories)
    headers = {'X-Yandex-Uid': user_id}
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER, request_body, headers=headers,
    )
    assert response.status_code == 200
    for result_cat in response.json()['payload']['categories']:
        result_items = [entry['id'] for entry in result_cat['items']]
        assert expected_categories[result_cat.get('id')] == result_items


@util.get_sort_exp3_with_value('random')
@pytest.mark.parametrize(
    'user_id,input_categories',
    [
        pytest.param('device1', {1: [1, 2, 3, 4, 5]}, id='single_category'),
        pytest.param(
            'device2',
            {1: [1, 2, 3, 4], 2: [8, 7, 6, 5]},
            id='multiple_categories',
        ),
    ],
)
async def test_random_sort_same_day(
        taxi_eats_restaurant_menu, mocked_time, user_id, input_categories,
):
    request_body = get_request_body(input_categories)
    headers = {'X-Yandex-Uid': user_id}

    mocked_time.set(datetime.datetime(2020, 11, 15, 12, 0, 0))
    await taxi_eats_restaurant_menu.invalidate_caches()
    response_now = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER, request_body, headers=headers,
    )
    assert response_now.status_code == 200
    mocked_time.set(datetime.datetime(2020, 11, 15, 13, 0, 0))
    await taxi_eats_restaurant_menu.invalidate_caches()
    response_in_hour = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER, request_body, headers=headers,
    )
    assert response_in_hour.status_code == 200

    assert response_now.json() == response_in_hour.json()


@util.get_sort_exp3_with_value('random')
@pytest.mark.parametrize(
    'user_id,input_categories',
    [
        pytest.param('device1', {1: [1, 2, 3, 4, 5]}, id='single_category'),
        pytest.param(
            'device2',
            {1: [1, 2, 3, 4], 2: [8, 7, 6, 5]},
            id='multiple_categories',
        ),
    ],
)
async def test_random_sort_other_day(
        taxi_eats_restaurant_menu, mocked_time, user_id, input_categories,
):
    request_body = get_request_body(input_categories)
    headers = {'X-Yandex-Uid': user_id}

    mocked_time.set(datetime.datetime(2020, 11, 15, 12, 0, 0))
    await taxi_eats_restaurant_menu.invalidate_caches()
    response_today = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER, request_body, headers=headers,
    )
    assert response_today.status_code == 200
    mocked_time.set(datetime.datetime(2020, 11, 16, 12, 0, 0))
    await taxi_eats_restaurant_menu.invalidate_caches()
    response_next_day = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER, request_body, headers=headers,
    )
    assert response_next_day.status_code == 200

    assert response_today.json() != response_next_day.json()
    today_cats = response_today.json()['payload']['categories']
    next_cats = response_next_day.json()['payload']['categories']

    for cat in today_cats:
        other = next(
            entry for entry in next_cats if entry['id'] == cat.get('id')
        )
        assert set(item['id'] for item in cat['items']) == set(
            item['id'] for item in other['items']
        )
