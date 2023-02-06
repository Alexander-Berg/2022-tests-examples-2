import pytest

from typing import List
from typing import Optional
from typing import Union
from datetime import datetime
from tests_grocery_discounts import common


COUNTRY = 'RUS'
CITY = '213'
DEPOT = '71249'
PRODUCT = '3f9d763ee2594b7088d53bc5d1aef1af000200010001'
GROUP = '7fd91f0cc9e9494a9cf2c124ce94695d000200010001'
EXPERIMENT = 'promo_grp_1'
YANDEX_UID = 1
PERSONAL_PHONE_ID = 'ppee11'

START_DATA_ID = '123'

NOW_STR = '2019-01-01T00:00:00+00:00'

MENU_RULES = [
    {
        'condition_name': 'active_period',
        'values': [
            {
                'start': '2020-01-01T09:00:01+00:00',
                'is_start_utc': False,
                'end': '2021-01-01T00:00:00+00:00',
                'is_end_utc': False,
            },
        ],
    },
    {'condition_name': 'city', 'values': [CITY]},
    {'condition_name': 'depot', 'values': [DEPOT]},
    {'condition_name': 'country', 'values': [COUNTRY]},
    {'condition_name': 'experiment', 'values': [EXPERIMENT]},
    {'condition_name': 'product', 'values': [PRODUCT]},
    {'condition_name': 'group', 'values': [GROUP]},
]


def _get_request(hierarchy_name: str) -> dict:
    return {
        'hierarchy_names': [hierarchy_name],
        'common_conditions': {
            'request_time': '2020-02-01T09:00:01+00:00',
            'request_timezone': 'UTC',
            'experiments': [EXPERIMENT],
            'depots': [DEPOT],
            'cities': [CITY],
            'countries': [COUNTRY],
            'personal_phone_id': PERSONAL_PHONE_ID,
        },
        'subqueries': [
            {
                'subquery_id': PRODUCT,
                'conditions': {'product': PRODUCT, 'groups': [GROUP]},
            },
        ],
    }


def _get_response(
        found_expected: bool, has_discount_usage_restrictions: bool = False,
) -> dict:
    if found_expected:
        result: dict = {
            'match_results': [
                {
                    'results': [
                        {
                            'discounts': [
                                {
                                    'create_draft_id': (
                                        'draft_id_check_add_rules_validation'
                                    ),
                                    'discount': {
                                        'active_with_surge': False,
                                        'discount_id': START_DATA_ID,
                                        'discount_meta': {
                                            'informer': {
                                                'color': (
                                                    'menu_discounts_color'
                                                ),
                                                'picture': (
                                                    'menu_discounts_picture'
                                                ),
                                                'text': 'menu_discounts_text',
                                            },
                                        },
                                        'money_value': {
                                            'menu_value': {
                                                'value_type': 'absolute',
                                                'value': '1.5',
                                            },
                                        },
                                    },
                                },
                            ],
                            'hierarchy_name': 'menu_discounts',
                            'status': 'ok',
                        },
                    ],
                    'subquery_id': PRODUCT,
                },
            ],
            'restoration_info': {
                'versions': [{'id': 'default', 'name': 'rules-match-cache'}],
            },
        }
        if has_discount_usage_restrictions:
            result['match_results'][0]['results'][0]['discounts'][0][
                'discount'
            ]['has_discount_usage_restrictions'] = True
        return result
    return {
        'match_results': [
            {
                'subquery_id': PRODUCT,
                'results': [
                    {
                        'status': 'ok',
                        'discounts': [],
                        'hierarchy_name': 'menu_discounts',
                    },
                ],
            },
        ],
        'restoration_info': {
            'versions': [{'name': 'rules-match-cache', 'id': 'default'}],
        },
    }


def _get_headers() -> dict:
    headers = dict(common.get_headers())
    headers['X-Yandex-UID'] = str(YANDEX_UID)
    return headers


async def _add_discount_usage(
        stq_runner,
        add_time: str,
        usage_count: int,
        add_personal_phone_id: bool = False,
):
    for i in range(usage_count):
        kwargs = {
            'order_id': f'test_order_id_{i}',
            'discount_ids': [START_DATA_ID],
            'add_time': add_time,
            'yandex_uid': YANDEX_UID,
        }

        if add_personal_phone_id:
            kwargs['personal_phone_id'] = PERSONAL_PHONE_ID

        await stq_runner.grocery_discounts_discount_usage_add.call(
            task_id=f'test_order_id_{i}_{YANDEX_UID}', kwargs=kwargs,
        )


@pytest.mark.now(NOW_STR)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules',
    (pytest.param('menu_discounts', MENU_RULES, id='menu_discounts'),),
)
async def test_v4_match_discounts(
        client, check_add_rules_validation, hierarchy_name, rules, headers,
):
    discount = common.small_menu_discount()
    discount['active_with_surge'] = False

    is_check = False
    await check_add_rules_validation(
        is_check, {'revisions': []}, hierarchy_name, rules, discount,
    )
    await client.post(
        '/v1/admin/groups', headers=headers, json={'groups': [GROUP]},
    )

    await client.invalidate_caches()
    response = await client.post(
        'v4/match-discounts/',
        headers=_get_headers(),
        json=_get_request(hierarchy_name),
    )
    assert response.status == 200, response.json()

    assert response.json() == _get_response(True)


@pytest.mark.parametrize(
    'discount_usage_restrictions, need_return_discount, '
    'config_enabled, add_personal_phone_id',
    (
        pytest.param(
            [{'max_count': 3}],
            True,
            True,
            False,
            id='none_interval_3_enabled',
        ),
        pytest.param(
            [{'max_count': 3}],
            False,
            False,
            False,
            id='none_interval_3_disabled',
        ),
        pytest.param(
            [{'max_count': 1}],
            False,
            True,
            False,
            id='none_interval_1_enabled',
        ),
        pytest.param(
            [{'max_count': 3}],
            True,
            True,
            True,
            id='none_interval_3_enabled_personal_phone',
        ),
        pytest.param(
            [{'max_count': 1}],
            False,
            True,
            True,
            id='none_interval_1_enabled_personal_phone',
        ),
        pytest.param(
            [{'max_count': 1, 'interval': 10}],
            False,
            False,
            False,
            id='too_small_interval_1_enabled',
        ),
        pytest.param(
            [{'max_count': 1, 'interval': 100500}],
            False,
            False,
            False,
            id='big_enough_interval_1_enabled',
        ),
        pytest.param(None, True, True, False, id='does_not_have_restriction'),
    ),
)
@pytest.mark.now(NOW_STR)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_v4_match_discounts_restricted_by_discount_usage(
        client,
        stq_runner,
        taxi_config,
        mocked_time,
        check_add_rules_validation,
        headers,
        discount_usage_restrictions,
        need_return_discount,
        config_enabled,
        add_personal_phone_id,
):
    rules = MENU_RULES
    hierarchy_name = 'menu_discounts'

    taxi_config.set(
        GROCERY_DISCOUNTS_FETCH_DATA_SETTINGS={
            'discount_usages': {'enabled': config_enabled},
        },
    )

    discount = common.small_menu_discount()
    discount['active_with_surge'] = False
    if discount_usage_restrictions:
        discount['discount_usage_restrictions'] = discount_usage_restrictions

    is_check = False
    await check_add_rules_validation(
        is_check, {'revisions': []}, hierarchy_name, rules, discount,
    )
    await client.post(
        '/v1/admin/groups', headers=headers, json={'groups': [GROUP]},
    )

    await _add_discount_usage(stq_runner, NOW_STR, 2, add_personal_phone_id)

    await client.invalidate_caches()

    response = await client.post(
        'v4/match-discounts/',
        headers=_get_headers(),
        json=_get_request(hierarchy_name),
    )
    assert response.status == 200, response.json()

    assert response.json() == _get_response(
        need_return_discount, bool(discount_usage_restrictions),
    )


@pytest.mark.parametrize(
    'active_with_surge, has_surge, found_discounts_count',
    (
        pytest.param(1, True, 1, id='active_with_surge'),
        pytest.param(1, False, 1, id='active_without_surge'),
        pytest.param(0, True, 0, id='inactive_with_surge'),
        pytest.param(0, False, 1, id='inactive_without_surge'),
    ),
)
@pytest.mark.now(NOW_STR)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
async def test_v4_match_discounts_surge(
        client,
        check_add_rules_validation,
        headers,
        active_with_surge,
        has_surge,
        found_discounts_count,
):
    hierarchy_name = 'cart_discounts'
    discount = common.small_cart_discount()
    rules = MENU_RULES.copy()
    if not active_with_surge:
        rules += [
            {
                'condition_name': 'active_with_surge',
                'values': [active_with_surge],
            },
        ]

    is_check = False
    await check_add_rules_validation(
        is_check, {'revisions': []}, hierarchy_name, rules, discount,
    )
    request = _get_request(hierarchy_name)
    request['common_conditions']['has_surge'] = has_surge
    await client.invalidate_caches()
    response = await client.post(
        'v4/match-discounts/', headers=_get_headers(), json=request,
    )

    assert response.status == 200
    assert (
        len(response.json()['match_results'][0]['results'][0]['discounts'])
        == found_discounts_count
    ), response.json()


@pytest.mark.parametrize(
    'discount_master_group, discount_exclusions_master_group, match',
    (
        pytest.param('Other', None, True),
        pytest.param(['master_group_4'], None, False),
        pytest.param(['master_group_2'], None, True),
        pytest.param('Other', ['master_group_2'], False),
        pytest.param('Other', ['master_group_4'], True),
    ),
)
@pytest.mark.now(NOW_STR)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
async def test_v4_match_discounts_master_group(
        client,
        load_json,
        add_rules,
        mocked_time,
        discount_master_group: Union[str, List[str]],
        discount_exclusions_master_group: Optional[List[str]],
        match: bool,
):
    add_rules_request = common.get_add_rules_data(
        hierarchy_names=['menu_discounts'],
    )
    master_group_condition = {
        'condition_name': 'master_group',
        'values': discount_master_group,
    }
    if discount_exclusions_master_group:
        master_group_condition['exclusions'] = discount_exclusions_master_group
    add_rules_request['menu_discounts'][0]['rules'].append(
        master_group_condition,
    )
    await add_rules(add_rules_request)

    mocked_time.set(datetime.fromisoformat('2020-02-01T10:00:00+00:00'))
    await client.invalidate_caches()

    request_match_discounts = load_json('request_match_discounts.json')
    response = await client.post(
        'v4/match-discounts/',
        headers=_get_headers(),
        json=request_match_discounts,
    )

    assert response.status == 200
    assert len(
        response.json()['match_results'][0]['results'][0]['discounts'],
    ) == int(match), response.json()
