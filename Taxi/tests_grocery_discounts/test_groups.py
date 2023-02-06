import datetime
import json
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from grocery_discounts_plugins.generated_tests import *  # noqa

GROUPS_CHECK_URL = '/v3/admin/groups/check'


async def _get_groups(taxi_grocery_discounts, expected_body: dict) -> None:
    response = await taxi_grocery_discounts.get(
        common.GROUPS_URL, headers=common.get_headers(),
    )
    assert response.status_code == 200
    assert response.json() == expected_body


async def _post_groups_check(
        taxi_grocery_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
        expected_old_groups: Optional[list] = None,
) -> None:
    response = await taxi_grocery_discounts.post(
        GROUPS_CHECK_URL, request, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        lock_ids: List[dict] = [
            {'id': item['root_name'], 'custom': True}
            for item in request['groups_orders']
        ]
        if expected_old_groups is None:
            expected_old_groups = []
        assert response.json() == {
            'lock_ids': lock_ids,
            'data': request,
            'diff': {
                'current': {'groups_orders': expected_old_groups},
                'new': request,
            },
        }
    elif expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_service_with_db(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.get('ping')
    assert response.status_code == 200
    assert response.content == b''
    await taxi_grocery_discounts.invalidate_caches()


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_get_groups_in_orger(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.get(
        'v1/admin/groups', headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['groups'] == ['Ready meals', 'Meat', 'Sweets']


@pytest.mark.servicetest
@pytest.mark.parametrize('url', ['/v1/admin/groups', '/v1/admin/groups/check'])
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_post_groups_in_orger(taxi_grocery_discounts, url):
    data = {'groups': ['Meat', 'Sweets', 'Wheel-chairs']}
    response = await taxi_grocery_discounts.post(
        '/v1/admin/groups',
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps(data),
    )

    assert response.status_code == 200

    response = await taxi_grocery_discounts.get(
        'v1/admin/groups', headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['groups'] == ['Meat', 'Sweets', 'Wheel-chairs']


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'body, expected_status_code, expected_content',
    (
        (
            {'groups': ['Meat', 'Sweets', 'Wheel-chairs']},
            200,
            {
                'change_doc_id': 'groups',
                'data': {'groups': ['Meat', 'Sweets', 'Wheel-chairs']},
            },
        ),
        (
            {'groups': ['Meat', 'Wheel-chairs']},
            400,
            {
                'code': 'Postgres error',
                'message': 'Some missing groups still uses in discounts',
            },
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_check_post_groups_in_orger(
        taxi_grocery_discounts, body, expected_status_code, expected_content,
):
    response = await taxi_grocery_discounts.post(
        '/v1/admin/groups/check',
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps(body),
    )

    assert response.status_code == expected_status_code
    response_json = response.json()
    assert response_json == expected_content


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_get_named_groups_in_orger(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.get(
        'v3/admin/groups', headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['groups_orders'] == [
        {'root_name': 'root1', 'groups': ['group1', 'group2']},
        {'root_name': 'root2', 'groups': ['group3', 'group1']},
    ]


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
@pytest.mark.now('2020-07-22T08:00:00')
async def test_save_named_groups(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.post(
        '/v3/admin/groups',
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps(
            {
                'groups_orders': [
                    {'root_name': 'root1', 'groups': ['group2']},
                    {'root_name': 'root3', 'groups': ['group3', 'group1']},
                    {
                        'root_name': 'root2',
                        'groups': ['group2', 'group3', 'group1'],
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert response.json() == {
        'groups_orders': [
            {'root_name': 'root1', 'groups': ['group2']},
            {'root_name': 'root3', 'groups': ['group3', 'group1']},
            {'root_name': 'root2', 'groups': ['group2', 'group3', 'group1']},
        ],
    }

    response = await taxi_grocery_discounts.get(
        '/v3/admin/groups', headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'groups_orders': [
            {'root_name': 'root1', 'groups': ['group2']},
            {'root_name': 'root2', 'groups': ['group2', 'group3', 'group1']},
            {'root_name': 'root3', 'groups': ['group3', 'group1']},
        ],
    }


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True)
async def test_groups(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    groups_0 = {'groups_orders': []}
    await _get_groups(taxi_grocery_discounts, groups_0)

    groups_1 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_1', 'group_2']},
            {'root_name': 'second_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    await common.set_groups(taxi_grocery_discounts, groups_1)
    await _get_groups(taxi_grocery_discounts, groups_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await common.set_groups(taxi_grocery_discounts, groups_0)
    await _get_groups(taxi_grocery_discounts, groups_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_2 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_6', 'group_7']},
            {'root_name': 'third_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    groups_result_1 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_6', 'group_7']},
            {'root_name': 'second_root', 'groups': ['group_4', 'group_5']},
            {'root_name': 'third_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    await common.set_groups(taxi_grocery_discounts, groups_2)
    await _get_groups(taxi_grocery_discounts, groups_result_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_3 = {
        'groups_orders': [{'root_name': '', 'groups': ['group_6', 'group_7']}],
    }
    await common.set_groups(taxi_grocery_discounts, groups_3, 400)
    await _get_groups(taxi_grocery_discounts, groups_result_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_4 = {
        'groups_orders': [{'root_name': 'fourth_root', 'groups': ['']}],
    }
    await common.set_groups(taxi_grocery_discounts, groups_4, 400)
    await _get_groups(taxi_grocery_discounts, groups_result_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_5 = {'groups_orders': [{'root_name': 'first_root', 'groups': []}]}
    groups_result_2 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': []},
            {'root_name': 'second_root', 'groups': ['group_4', 'group_5']},
            {'root_name': 'third_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    await common.set_groups(taxi_grocery_discounts, groups_5)
    await _get_groups(taxi_grocery_discounts, groups_result_2)

    now -= datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_6 = {
        'groups_orders': [{'root_name': 'first_root', 'groups': ['group_8']}],
    }
    await common.set_groups(taxi_grocery_discounts, groups_6)
    await _get_groups(taxi_grocery_discounts, groups_result_2)


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True)
async def test_groups_check(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    groups_0 = {'groups_orders': []}
    await _get_groups(taxi_grocery_discounts, groups_0)

    groups_1 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_1', 'group_2']},
            {'root_name': 'second_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    await _post_groups_check(taxi_grocery_discounts, groups_1)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_groups_check(taxi_grocery_discounts, groups_0)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_2 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_6', 'group_7']},
            {'root_name': 'third_root', 'groups': ['group_4', 'group_5']},
        ],
    }
    await _post_groups_check(taxi_grocery_discounts, groups_2)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_3 = {
        'groups_orders': [{'root_name': '', 'groups': ['group_6', 'group_7']}],
    }
    await _post_groups_check(taxi_grocery_discounts, groups_3, 400)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_4 = {
        'groups_orders': [{'root_name': 'fourth_root', 'groups': ['']}],
    }
    await _post_groups_check(taxi_grocery_discounts, groups_4, 400)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_5 = {'groups_orders': [{'root_name': 'first_root', 'groups': []}]}
    await _post_groups_check(taxi_grocery_discounts, groups_5)
    await _get_groups(taxi_grocery_discounts, groups_0)

    now -= datetime.timedelta(seconds=1)
    mocked_time.set(now)
    groups_6 = {
        'groups_orders': [{'root_name': 'first_root', 'groups': ['group_8']}],
    }
    await _post_groups_check(taxi_grocery_discounts, groups_6)
    await _get_groups(taxi_grocery_discounts, groups_0)


@pytest.mark.parametrize(
    'hierarchy_name, expected_body, expected_status_code',
    (
        pytest.param('cart_discounts', None, 200, id='cart_discounts'),
        pytest.param(
            'menu_discounts',
            {
                'code': 'Validation error',
                'message': (
                    'Some of entity values are used in possibly active '
                    'discounts: {"condition_name":"group",'
                    '"values":["group_2"]}'
                ),
            },
            400,
            id='menu_discounts',
        ),
        pytest.param(
            'payment_method_discounts',
            {
                'code': 'Validation error',
                'message': (
                    'Some of entity values are used in possibly active '
                    'discounts: {"condition_name":"group",'
                    '"values":["group_2"]}'
                ),
            },
            400,
            id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.GROUPS_URL, id='groups'),
        pytest.param(GROUPS_CHECK_URL, id='check_groups'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_groups_references(
        taxi_grocery_discounts,
        mocked_time,
        handler: str,
        hierarchy_name: str,
        expected_status_code: int,
        expected_body: Optional[dict],
        add_rules,
):
    groups_1 = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_1', 'group_2']},
            {'root_name': 'second_root', 'groups': ['group_3', 'group_4']},
        ],
    }
    await common.set_groups(taxi_grocery_discounts, groups_1)

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    add_rules_data = common.get_add_rules_data()
    add_rules_data[hierarchy_name][0]['rules'].append(
        {'condition_name': 'group', 'values': ['group_2']},
    )
    await add_rules(add_rules_data)

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    groups = {
        'groups_orders': [
            {'root_name': 'first_root', 'groups': ['group_1']},
            {
                'root_name': 'second_root',
                'groups': ['group_2', 'group_3', 'group_4'],
            },
        ],
    }

    await taxi_grocery_discounts.invalidate_caches()
    if handler == common.GROUPS_URL:
        await common.set_groups(
            taxi_grocery_discounts,
            groups,
            expected_status_code,
            expected_body,
        )
    else:
        await _post_groups_check(
            taxi_grocery_discounts,
            groups,
            expected_status_code,
            expected_body,
            groups_1['groups_orders'],
        )
