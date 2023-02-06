import copy
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Set

# Generated via `tvmknife unittest service -s 123 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIexCpEg:PkDHYmG'
    'PZmF01QRRlgate8JvdS2HrShQxHIsr9x3tuUSrcex'
    '_RkAId_QbiPURL8oSGUscDwFiDgBde0ZAFsj_Qq1h'
    'NnCSnAV_ygcAY2a_hoIIQzDhcUKtHgmS7x5YjTaog'
    'BHVF3ZC6lrWfqwmAxdGsavk_3ncMXJxDM25ygJK6Y'
)

PRIORITIZED_ENTITY_URL = '/v1/admin/prioritized-entity/'
PRIORITY_CHECK_URL = '/v1/admin/prioritized-entity/check/'
PRIORITY_URL = '/v1/admin/priority/'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_SCHEDULE = {
    'timezone': 'LOCAL',
    'intervals': [{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}],
}

VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:01+00:00',
            'is_start_utc': True,
            'is_end_utc': True,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}

ADD_RULES_URL = 'v1/admin/match-discounts/add-rules'
ADD_RULES_CHECK_URL = 'v1/admin/match-discounts/add-rules/check'

BIN_SET_URL = '/v1/admin/bin-set'
BIN_SETS_PRIORITY_URL = '/v1/admin/bin-sets-priority'


SERIES_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
TASK_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

START_DATA_ID = '123'
START_REVISION = 22


def get_discount_meta() -> dict:
    return {
        'promo': {
            'name': 'name_tanker_key',
            'description': 'description_tanker_key',
            'picture_uri': 'picture_uri',
        },
    }


def get_headers():
    return {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-YaTaxi-Draft-Tickets': 'ticket-1',
        'X-YaRequestId': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
    }


def get_draft_headers(draft_id: Optional[str] = None):
    return {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-YaTaxi-Draft-Author': 'user',
        'X-YaTaxi-Draft-Tickets': 'ticket-1',
        'X-YaRequestId': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
        'X-YaTaxi-Draft-Id': (
            draft_id if draft_id else 'eats_discounts_draft_id'
        ),
    }


def get_revision(pgsql) -> int:
    pg_cursor = pgsql['eats_discounts'].cursor()
    pg_cursor.execute(
        f"""SELECT last_value
            FROM eats_discounts.match_rules_revision;""",
    )
    return list(pg_cursor)[0][0]


async def set_priority(
        taxi_eats_discounts,
        request_body: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.post(
        PRIORITY_URL,
        request_body,
        headers=get_draft_headers('draft_id_test_admin_priority'),
    )
    assert response.status_code == expected_status_code
    response_json = response.json()
    if expected_status_code == 200:
        response_json['priority_groups'].sort(key=lambda group: group['name'])
        assert response_json == request_body
    elif expected_body is not None:
        assert response_json == expected_body


def small_menu_discount(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'product_value': {'discount_value': '1.5', 'bundle': 2},
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': get_discount_meta(),
    }


def small_retail_menu_discount(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'product_value': {'discount_value': '1.5', 'bundle': 2},
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': get_discount_meta(),
    }


def small_cart_discount(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'money_value': {
                    'set_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': get_discount_meta(),
    }


def small_payment_method_discount(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'product_value': {'discount_value': '1.6', 'bundle': 3},
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': get_discount_meta(),
    }


def small_place_menu_cashback(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'cashback_value': {
                    'menu_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10.0',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {'name': 'name'},
    }


def small_place_delivery_discount(name: str = '1') -> dict:
    return {
        'name': name,
        'values_with_schedules': [
            {
                'money_value': {
                    'menu_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10.0',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': get_discount_meta(),
    }


def small_yandex_delivery_discount(name: str = '1') -> dict:
    return small_place_delivery_discount(name)


def small_place_cashback(name: str = '1') -> dict:
    return small_place_menu_cashback(name)


def small_yandex_cashback(name: str = '1') -> dict:
    return small_place_menu_cashback(name)


def small_yandex_menu_cashback(name: str = '1') -> dict:
    return small_place_menu_cashback(name)


def _make_response_matched_discounts(discounts: List[dict]) -> int:
    """
    Returns maximal encountered revision or 0
    """
    max_revision = 0
    for discount in discounts:
        match_parameters = discount.get('match_parameters')
        if match_parameters:
            revision = match_parameters.pop('revision')
            assert isinstance(revision, int)
            if revision > max_revision:
                max_revision = revision
            match_parameters['match_path'].sort(
                key=lambda condition: condition['condition_name'],
            )
    discounts.sort(key=lambda discount: discount['discount'].get('name'))
    return max_revision


def make_response_matched_results(match_results: List[dict]) -> None:
    match_results.sort(key=lambda result: result['hierarchy_name'])
    for result in match_results:
        _make_response_matched_discounts(result['discounts'])


def make_expected_matched_results(
        match_results: List[dict],
        unique_hierarchy_names: Set[str],
        show_match_parameters: bool,
) -> List[dict]:
    match_results = [
        result
        for result in match_results
        if result['hierarchy_name'] in unique_hierarchy_names
    ]
    for match_result in match_results:
        for discount in match_result['discounts']:
            if not show_match_parameters:
                discount.pop('match_parameters')
    return match_results


def active_period_value(active_period: dict) -> dict:
    return {
        'condition_name': active_period['condition_name'],
        'value': active_period['values'][0],
    }


def get_added_discount(
        add_rules_data: dict, hierarchy_name: str, add_index: int = 0,
) -> dict:
    discount = copy.deepcopy(
        add_rules_data[hierarchy_name][add_index]['discount'],
    )
    return discount


def get_matched_discount(
        add_rules_data: dict,
        hierarchy_name: str,
        matched_index: int = 0,
        add_index: int = 0,
) -> dict:
    discount = get_added_discount(add_rules_data, hierarchy_name, add_index)
    result: dict = {'name': discount['name'], 'series_id': SERIES_ID}

    discount_meta = discount.get('discount_meta')
    if discount_meta is not None:
        result['discount_meta'] = discount_meta

    matched_value = discount['values_with_schedules'][matched_index]

    product_value = matched_value.get('product_value')
    if product_value is not None:
        result['product_value'] = product_value

    cashback_value = matched_value.get('cashback_value')
    if cashback_value is not None:
        result['cashback_value'] = cashback_value

    money_value = matched_value.get('money_value')
    if money_value is not None:
        result['money_value'] = money_value

    return result


def cart_match_path(active_period: Optional[dict] = None) -> dict:

    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'product_set', 'value': []},
            {'condition_name': 'region', 'value': 123},
        ],
    }


def menu_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'product', 'value_type': 'Other'},
            {'condition_name': 'region', 'value': 123},
        ],
    }


def payment_method_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'bins', 'value_type': 'Other'},
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'payment_method', 'value_type': 'Other'},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'region', 'value': 123},
        ],
    }


def place_menu_cashback_match_path(
        active_period: Optional[dict] = None,
) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'orders_count', 'value_type': 'Other'},
            {'condition_name': 'places_count', 'value_type': 'Other'},
            {'condition_name': 'region', 'value': 123},
            {'condition_name': 'yaplus_level', 'value_type': 'Other'},
        ],
    }


def place_cashback_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'cashback_subventon', 'value_type': 'Other'},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'place_cashback', 'value_type': 'Other'},
            {
                'condition_name': 'place_cashback_commission',
                'value_type': 'Other',
            },
            {'condition_name': 'place_cashback_days', 'value_type': 'Other'},
            {'condition_name': 'place_has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'place_orders_count', 'value_type': 'Other'},
            {'condition_name': 'product', 'value_type': 'Other'},
            {'condition_name': 'surge_range', 'value_type': 'Other'},
        ],
    }


def yandex_cashback_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'check', 'value_type': 'Other'},
            {'condition_name': 'payment_method', 'value_type': 'Other'},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'region', 'value': 123},
        ],
    }


def yandex_menu_cashback_match_path(
        active_period: Optional[dict] = None,
) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'delivery', 'value_type': 'Other'},
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'place', 'value': 456},
            {'condition_name': 'place_has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'region', 'value': 123},
            {'condition_name': 'yaplus_level', 'value_type': 'Other'},
        ],
    }


def delivery_discounts_match_path(
        active_period: Optional[dict] = None,
) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'region', 'value': 123},
            {'condition_name': 'brand', 'value': 321},
            {'condition_name': 'place', 'value': 456},
        ],
    }


def get_match_path(
        hierarchy_name: str, active_period: Optional[dict] = None,
) -> dict:
    if hierarchy_name == 'cart_discounts':
        return cart_match_path(active_period)
    if hierarchy_name == 'menu_discounts':
        return menu_match_path(active_period)
    if hierarchy_name == 'payment_method_discounts':
        return payment_method_match_path(active_period)
    if hierarchy_name == 'place_menu_cashback':
        return place_menu_cashback_match_path(active_period)
    if hierarchy_name == 'place_cashback':
        return place_cashback_match_path(active_period)
    if hierarchy_name == 'yandex_cashback':
        return yandex_cashback_match_path(active_period)
    if hierarchy_name == 'yandex_menu_cashback':
        return yandex_menu_cashback_match_path(active_period)
    if hierarchy_name == 'retail_menu_discounts':
        return menu_match_path(active_period)
    if hierarchy_name == 'place_delivery_discounts':
        return delivery_discounts_match_path(active_period)
    if hierarchy_name == 'yandex_delivery_discounts':
        return delivery_discounts_match_path(active_period)
    raise Exception(f'Unsupported hierarhy {hierarchy_name}')


def get_add_rules_data(
        active_period: Optional[dict] = None,
        hierarchy_names: FrozenSet[str] = frozenset(
            ('cart_discounts', 'menu_discounts', 'payment_method_discounts'),
        ),
        name: str = '1',
) -> dict:
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    rules = [
        active_period,
        {'condition_name': 'brand', 'values': [321]},
        {'condition_name': 'place', 'values': [456]},
        {'condition_name': 'region', 'values': [123]},
    ]
    result = dict()
    if 'cart_discounts' in hierarchy_names:
        result['cart_discounts'] = [
            {'rules': rules, 'discount': small_cart_discount(name)},
        ]
    if 'menu_discounts' in hierarchy_names:
        result['menu_discounts'] = [
            {
                'rules': copy.deepcopy(rules),
                'discount': small_menu_discount(name),
            },
        ]
    if 'payment_method_discounts' in hierarchy_names:
        result['payment_method_discounts'] = [
            {
                'rules': copy.deepcopy(rules),
                'discount': small_payment_method_discount(name),
            },
        ]
    return result


def get_full_add_rules_data(active_period: Optional[dict] = None):
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    rules = [
        active_period,
        {'condition_name': 'brand', 'values': [321]},
        {'condition_name': 'place', 'values': [456]},
        {'condition_name': 'region', 'values': [123]},
    ]
    return {
        'menu_discounts': [
            {
                'rules': rules,
                'discount': {
                    'name': '1',
                    'discount_meta': get_discount_meta(),
                    'values_with_schedules': [
                        {
                            'product_value': {
                                'discount_value': '1.5',
                                'bundle': 2,
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '10.0',
                                },
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [{'exclude': False, 'day': [5]}],
                            },
                        },
                        {
                            'product_value': {
                                'discount_value': '1',
                                'bundle': 3,
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {
                                        'exclude': False,
                                        'day': [1, 2, 3, 4, 6, 7],
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ],
        'cart_discounts': [
            {
                'rules': rules,
                'discount': {
                    'name': '2',
                    'discount_meta': get_discount_meta(),
                    'values_with_schedules': [
                        {
                            'product_value': {
                                'value': [
                                    {
                                        'step': {
                                            'from_cost': '13',
                                            'discount': '7',
                                        },
                                        'products': [{'id': 'some_product'}],
                                        'bundle': 100,
                                    },
                                ],
                            },
                            'money_value': {
                                'set_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '10',
                                },
                                'cart_value': {
                                    'maximum_discount': '500',
                                    'value': [
                                        {
                                            'from_cost': '14',
                                            'discount': {
                                                'value_type': 'fraction',
                                                'value': '8',
                                            },
                                        },
                                    ],
                                },
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {'exclude': False, 'day': [2, 3, 5]},
                                ],
                            },
                        },
                        {
                            'money_value': {
                                'set_value': {
                                    'value_type': 'absolute',
                                    'value': '11.0',
                                },
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {'exclude': False, 'day': [1, 4, 6, 7]},
                                ],
                            },
                        },
                    ],
                },
            },
        ],
        'payment_method_discounts': [
            {
                'rules': rules,
                'discount': {
                    'name': '3',
                    'discount_meta': get_discount_meta(),
                    'values_with_schedules': [
                        {
                            'product_value': {
                                'discount_value': '1.7',
                                'bundle': 10,
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '11.0',
                                },
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {'exclude': False, 'day': [4, 5]},
                                ],
                            },
                        },
                        {
                            'product_value': {
                                'discount_value': '0.8',
                                'bundle': 3,
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {'exclude': False, 'day': [1, 3, 6, 7]},
                                ],
                            },
                        },
                    ],
                },
            },
        ],
    }


async def add_bin_set(
        taxi_eats_discounts,
        request: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.post(
        BIN_SET_URL,
        request,
        headers=get_draft_headers('draft_id_test_admin_bin_set'),
    )
    assert response.status_code == expected_status_code
    response_json = response.json()
    if expected_status_code == 200:
        assert response_json == request
    elif expected_body is not None:
        assert response_json == expected_body


async def set_bin_sets_priority(
        taxi_eats_discounts,
        data: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.post(
        BIN_SETS_PRIORITY_URL,
        data,
        headers=get_draft_headers('draft_id_test_admin_bin_sets_priority'),
    )
    assert response.status_code == expected_status_code
    response_json = response.json()
    if expected_status_code == 200:
        assert response_json == data
    elif expected_body is not None:
        assert response_json == expected_body


async def init_bin_sets(taxi_eats_discounts) -> None:
    await add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'some_bins',
            'active_period': {
                'start': '2019-07-11T03:00:00',
                'end': '2021-07-18T03:00:00',
            },
            'bins': ['123321', '2344321'],
        },
    )
    await set_bin_sets_priority(
        taxi_eats_discounts, {'bin_sets_names': ['some_bins']},
    )


def get_task(task_id: str, pgsql) -> Optional[dict]:
    pg_cursor = pgsql['eats_discounts'].cursor()

    keys = (
        'task_id',
        'status',
        'message',
        'modified_at',
        'created_at',
        'task_result',
    )
    pg_cursor.execute(
        f"""SELECT *
            FROM eats_discounts.tasks
            WHERE task_id = '{task_id}'::UUID;""",
    )
    rows = list(pg_cursor)
    if rows:
        assert len(rows) == 1
        row = rows[0]
        result = dict(zip(keys, row))
        return result
    return None


def plan_task(task_id: str, pgsql, now, key: Optional[str] = None):
    pg_cursor = pgsql['eats_discounts'].cursor()
    pg_cursor.execute(
        f"""INSERT INTO eats_discounts.tasks (
                task_id, status, message, created_at, modified_at
            ) VALUES('{task_id}'::UUID, 'planned', NULL, '{now}', '{now}');""",
    )
    if key is None:
        return
    pg_cursor.execute(
        f"""INSERT INTO eats_discounts.unique_tasks (
                task_id, key
            ) VALUES('{task_id}'::UUID, '{key}');""",
    )


def add_unique_task(task_id: str, key: str, topic: str, pgsql):
    pg_cursor = pgsql['eats_discounts'].cursor()
    pg_cursor.execute(
        f"""INSERT INTO eats_discounts.unique_tasks (
                task_id, key, topic
            ) VALUES('{task_id}'::UUID, '{key}', '{topic}')
            ON CONFLICT ON CONSTRAINT unique_tasks_pkey DO UPDATE
              SET task_id = '{task_id}';
            ;""",
    )


def get_unique_task(key: str, topic: str, pgsql) -> Optional[str]:
    pg_cursor = pgsql['eats_discounts'].cursor()

    pg_cursor.execute(
        f"""SELECT task_id
            FROM eats_discounts.unique_tasks
            WHERE key = '{key}' and topic = '{topic}';""",
    )
    rows = list(pg_cursor)
    if rows:
        assert len(rows) == 1
        return rows[0][0]
    return None


def set_task_status(task_id: str, status: str, pgsql):
    pg_cursor = pgsql['eats_discounts'].cursor()

    pg_cursor.execute(
        f"""UPDATE eats_discounts.tasks
            SET status = '{status}'
            WHERE task_id = '{task_id}'::UUID;""",
    )


async def partners_discounts_create(
        stq_runner,
        pgsql,
        body: dict,
        task_id: str,
        expected_task_status: Optional[str],
        expected_task_message: Optional[str] = None,
):
    await stq_runner.eats_discounts_discounts_create.call(
        task_id=task_id, kwargs={'body': body},
    )
    task = get_task(task_id, pgsql)
    if expected_task_status is None:
        assert task is None
    else:
        assert task is not None
        assert task['status'] == expected_task_status
        assert task.get('message') == expected_task_message


def _prepare_admin_response(response: dict) -> dict:
    match_results: List[dict] = response['match_results']
    for match_result in match_results:
        conditions_groups = match_result['conditions_groups']
        conditions_groups.sort(
            key=lambda x: x.get('change_draft_id', '')
            + x.get('change_partner_user_id', '')
            + x.get('change_service_name', ''),
        )
        for conditions_group in conditions_groups:
            conditions_group['revisions'].sort()
            conditions = conditions_group['conditions']
            conditions.sort(key=lambda x: x['condition_name'])
            for condition in conditions:
                values = condition['values']
                if isinstance(values, List):
                    values.sort()
    return response


def compare_admin_responses(response: dict, expected_response: dict):
    assert _prepare_admin_response(response) == _prepare_admin_response(
        expected_response,
    )


async def check_admin_match_discounts(
        client,
        draft_headers,
        request: dict,
        expected_response: Optional[dict],
        expected_status_code: int,
):
    response = await client.post(
        '/v1/admin/match-discounts', json=request, headers=draft_headers,
    )

    assert response.status_code == expected_status_code, response.json()
    if expected_response is None:
        return
    if expected_status_code == 200:
        compare_admin_responses(response.json(), expected_response)
    else:
        assert response.json() == expected_response


async def check_admin_load_discounts(
        client,
        draft_headers,
        request: dict,
        expected_response: Optional[dict],
        expected_status_code: int,
):
    response = await client.post(
        '/v1/admin/load-discounts', json=request, headers=draft_headers,
    )

    assert response.status_code == expected_status_code, response.json()
    if expected_response is None:
        return
    if expected_status_code == 200:
        compare_admin_responses(response.json(), expected_response)
    else:
        assert response.json() == expected_response
