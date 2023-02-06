import copy
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_grocery_discounts import common

HIERARCHY_NAME = 'menu_discounts'

DEFAULT_FETCH_REQUEST = {
    'hierarchy_names': [HIERARCHY_NAME],
    'request_time': '2020-01-10T10:00:00+0000',  # Friday
    'request_timezone': 'UTC',
    'depot': 'some_depot',
    'city': '213',
    'country': 'russia',
    'iteration_number': 0,
}


async def _create_discounts(
        taxi_grocery_discounts, load_json, add_rules_path: str,
):
    new_discounts = load_json(add_rules_path)
    for new_discount in new_discounts:
        response = await taxi_grocery_discounts.post(
            'v3/admin/match-discounts/add-rules',
            new_discount,
            headers=common.DEFAULT_DISCOUNTS_HEADERS,
        )
        assert response.status_code == 200


def _get_expected_response(response_objects):
    products = []
    groups = []
    for response_object in response_objects:
        if isinstance(response_object, str):
            products.append(response_object)
        elif isinstance(response_object, list) and response_object:
            group = {'group_name': response_object[0]}
            if len(response_object) > 1:
                group['excluded_products'] = common.ListMixedObjects(
                    response_object[1],
                )
            groups.append(group)
    expected_response = {
        'items': [
            {
                'hierarchy_name': HIERARCHY_NAME,
                'products': common.ListMixedObjects(set(products)),
            },
        ],
    }
    if groups:
        expected_response['items'][0]['groups'] = common.ListMixedObjects(
            groups,
        )
    return expected_response


def _get_expected_responses(
        load_json, list_object_path: str, limit: Optional[int],
):
    response_objects = load_json(list_object_path)
    expected_responses = []
    index = 0
    while index < len(response_objects):
        objects = (
            response_objects
            if not limit
            else response_objects[index : index + limit]
        )
        response = _get_expected_response(objects)
        expected_responses.append(response)
        if limit is None:
            break
        index += limit
    return expected_responses


def _get_request(additional_fields: Dict[str, Any], limit: Optional[int]):
    request: Dict[str, Any] = copy.deepcopy(DEFAULT_FETCH_REQUEST)
    request.update(additional_fields)
    if limit:
        request['limit'] = limit
    return request


async def _check_fetch_discounted_products(
        taxi_grocery_discounts, request, expected_responses,
):
    response = await taxi_grocery_discounts.post(
        'v4/fetch-discounted-products/', request, headers=common.get_headers(),
    )
    assert response.status_code == 200
    response_json = response.json()
    count_iteration = response_json.pop('count_iteration')
    request['pagination_data'] = response_json.pop('pagination_data')
    assert response_json == expected_responses[0]
    request['iteration_number'] += 1
    while request['iteration_number'] < count_iteration:
        response = await taxi_grocery_discounts.post(
            'v4/fetch-discounted-products/',
            request,
            headers=common.get_headers(),
        )
        assert response.status_code == 200
        assert (
            response.json() == expected_responses[request['iteration_number']]
        )
        request['iteration_number'] += 1


async def _check_fetch_discounted_products_without_limit(
        taxi_grocery_discounts, request, expected_responses,
):
    response = await taxi_grocery_discounts.post(
        'v4/fetch-discounted-products/', request, headers=common.get_headers(),
    )
    assert response.status_code == 200
    assert [response.json()] == expected_responses


@pytest.mark.now('2020-01-01T06:00:00+0000')
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'add_rules_path, list_object_path, additional_fields',
    (
        pytest.param('add_discounts.json', 'list_objects.json', {}),
        pytest.param(
            'add_discounts_with_tags.json',
            'list_objects_with_tags.json',
            {'tags': ['tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']},
        ),
    ),
)
@pytest.mark.parametrize(
    'limit',
    (
        pytest.param(None),
        pytest.param(1),
        pytest.param(2),
        pytest.param(6),
        pytest.param(20),
        pytest.param(60),
        pytest.param(100),
    ),
)
async def test_fetch_discounted_products_v4(
        taxi_grocery_discounts,
        load_json,
        add_rules_path: str,
        list_object_path: str,
        additional_fields: Dict[str, Any],
        limit: Optional[int],
):
    await _create_discounts(taxi_grocery_discounts, load_json, add_rules_path)
    await taxi_grocery_discounts.invalidate_caches()
    expected_responses = _get_expected_responses(
        load_json, list_object_path, limit,
    )
    request = _get_request(additional_fields, limit)
    if limit:
        await _check_fetch_discounted_products(
            taxi_grocery_discounts, request, expected_responses,
        )
    else:
        await _check_fetch_discounted_products_without_limit(
            taxi_grocery_discounts, request, expected_responses,
        )


@pytest.mark.now('2020-01-01T06:00:00+0000')
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'add_rules_path, expected_responses, limit',
    (
        pytest.param(
            'add_discounts_many_hierarchies.json',
            [
                {
                    'items': [
                        {
                            'hierarchy_name': 'menu_discounts',
                            'products': common.ListMixedObjects(
                                {'product_1', 'product_2', 'product_3'},
                            ),
                        },
                    ],
                },
                {
                    'items': [
                        {
                            'hierarchy_name': 'menu_discounts',
                            'products': common.ListMixedObjects(
                                {'product_4', 'product_5', 'product_6'},
                            ),
                        },
                    ],
                },
                {
                    'items': [
                        {
                            'hierarchy_name': 'bundle_cashback',
                            'products': common.ListMixedObjects(
                                {'product_1', 'product_2', 'product_3'},
                            ),
                        },
                    ],
                },
            ],
            3,
        ),
    ),
)
async def test_fetch_discounted_products_v4_many_hierarchies(
        taxi_grocery_discounts,
        load_json,
        add_rules_path: str,
        expected_responses: str,
        limit: Optional[int],
):
    await _create_discounts(taxi_grocery_discounts, load_json, add_rules_path)
    await taxi_grocery_discounts.invalidate_caches()
    request = {
        'hierarchy_names': [
            'menu_discounts',
            'menu_cashback',
            'bundle_discounts',
            'bundle_cashback',
        ],
        'request_time': '2020-01-10T10:00:00+0000',  # Friday
        'request_timezone': 'UTC',
        'depot': 'some_depot',
        'city': '213',
        'country': 'russia',
        'iteration_number': 0,
        'limit': limit,
    }
    await _check_fetch_discounted_products(
        taxi_grocery_discounts, request, expected_responses,
    )
