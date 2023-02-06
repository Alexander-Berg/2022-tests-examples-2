# pylint: disable=too-many-lines
import copy
import datetime
from typing import Any
from typing import Dict
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

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_DISCOUNTS_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-YaTaxi-Draft-Author': 'user',
    'X-YaTaxi-Draft-Tickets': 'ticket-1',
    'X-YaTaxi-Draft-Id': 'unknown',
}


DEFAULT_SCHEDULE = {
    'timezone': 'LOCAL',
    'intervals': [{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}],
}

VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:01+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}

DEFAULT_CONFIGS = dict(
    GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
        'enabled': True,
    },
)

ADD_RULES_URL = 'v3/admin/match-discounts/add-rules'
ADD_RULES_CHECK_URL = 'v3/admin/match-discounts/add-rules/check'

BIN_SET_URL = '/v3/admin/bin-set'
BIN_SETS_PRIORITY_URL = '/v3/admin/bin-sets-priority'

CLASSES_URL = '/v3/admin/classes'

GROUPS_URL = '/v3/admin/groups'

CHANGE_RULES_END_TIME_URL = 'v3/admin/match-discounts/change-end-rules-time'
CHANGE_RULES_END_TIME_CHECK_URL = (
    'v3/admin/match-discounts/change-end-rules-time/check'
)

SERIES_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

TIME_IN_THE_PAST_ERROR = (
    'Time in the past for {}. The start time of the discount '
    'must be no earlier than the start time of the draft + delta. '
    'Delta: {} seconds.\nStart time of the draft + delta: {}. '
    'Discount start time: {}'
)


def check_discounts(response_json, subquery_id, hierarchy_name, discounts):
    make_match_discounts_response(response_json, False)
    subquery_results = next(
        item
        for item in response_json['match_results']
        if item['subquery_id'] == subquery_id
    )
    assert subquery_results['results']
    result = next(
        item
        for item in subquery_results['results']
        if item['hierarchy_name'] == hierarchy_name
    )
    assert result['status'] == 'ok'
    assert result['discounts'] == discounts, result['discounts']


def check_fetch_discounts(response_json, hierarchy_name, discounts):
    assert response_json['match_results']
    result = next(
        item
        for item in response_json['match_results']
        if item['hierarchy_name'] == hierarchy_name
    )
    assert result['status'] == 'ok'
    assert result['discounts'] == discounts


def remove_revision(input_json):
    assert input_json['match_results']
    for item in input_json['match_results']:
        for discount in item['discounts']:
            discount.pop('revision', None)
    return input_json


def remove_discount_id(input_json):
    assert input_json['match_results']
    for item in input_json['match_results']:
        for discount in item['discounts']:
            discount['discount'].pop('discount_id')
    return input_json


def get_headers():
    return {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


def get_draft_headers(draft_id: Optional[str] = None):
    return {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-YaTaxi-Draft-Author': 'user',
        'X-YaTaxi-Draft-Tickets': 'ticket-1',
        'X-YaTaxi-Draft-Id': (
            draft_id if draft_id else 'grocery_discounts_draft_id'
        ),
    }


def get_last_revision(pgsql, hierarchy) -> int:
    pg_cursor = pgsql['grocery_discounts'].cursor()
    pg_cursor.execute(
        f"""SELECT max(__revision)
            FROM grocery_discounts.match_rules_{hierarchy};""",
    )
    return list(pg_cursor)[0][0]


def get_revision(pgsql) -> int:
    pg_cursor = pgsql['grocery_discounts'].cursor()
    pg_cursor.execute(
        f"""SELECT last_value
            FROM grocery_discounts.match_rules_revision;""",
    )
    return list(pg_cursor)[0][0]


def small_menu_discount(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'money_value': {
                    'menu_value': {'value_type': 'absolute', 'value': '1.5'},
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {
            'informer': {
                'text': 'menu_discounts_text',
                'picture': 'menu_discounts_picture',
                'color': 'menu_discounts_color',
            },
        },
    }


def small_menu_cashback(description: str = '1') -> dict:
    return {
        'description': description,
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
        'discount_meta': {
            'informer': {
                'text': 'menu_cashback_text',
                'picture': 'menu_cashback_picture',
                'color': 'menu_cashback_color',
            },
        },
    }


def small_cart_discount(description: str = '1') -> dict:
    return {
        'description': description,
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
        'discount_meta': {
            'informer': {
                'text': 'cart_discounts_text',
                'picture': 'cart_discounts_picture',
                'color': 'cart_discounts_color',
            },
        },
    }


def small_cart_cashback(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'cashback_value': {
                    'set_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10.0',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {
            'informer': {
                'text': 'cart_cashback_text',
                'picture': 'cart_cashback_picture',
                'color': 'cart_cashback_color',
            },
        },
    }


def small_payment_method_discount(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'product_value': {'discount_value': '1.6', 'bundle': 3},
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {
            'informer': {
                'text': 'payment_method_discounts_text',
                'picture': 'payment_method_discounts_picture',
                'color': 'payment_method_discounts_color',
            },
        },
    }


def small_payment_method_cashback(description: str = '1') -> dict:
    return {
        'description': description,
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
        'discount_meta': {
            'informer': {
                'text': 'payment_method_cashback_text',
                'picture': 'payment_method_cashback_picture',
                'color': 'payment_method_cashback_color',
            },
        },
    }


def small_markdown_discount(description: str = '1') -> dict:
    return small_menu_discount(description)


def small_suppliers_discount(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'money_value': {
                    'menu_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {
            'informer': {
                'text': 'suppliers_discounts_text',
                'picture': 'suppliers_discounts_picture',
                'color': 'suppliers_discounts_color',
            },
        },
    }


def small_suppliers_cashback(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'cashback_value': {
                    'menu_value': {
                        'value_type': 'fraction',
                        'value': '10.0',
                        'maximum_discount': '10',
                    },
                },
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
        'discount_meta': {
            'informer': {
                'text': 'suppliers_discounts_text',
                'picture': 'suppliers_discounts_picture',
                'color': 'suppliers_discounts_color',
            },
        },
    }


def make_response_matched_discounts(discounts: List[dict]) -> int:
    """
    Returns maximal encountered revision or 0
    """
    max_revision = 0
    for discount in discounts:
        discount.pop('discount_id', None)
        revision = discount.get('revision')
        if revision:
            assert isinstance(revision, int)
            if revision > max_revision:
                max_revision = revision
            discount.pop('revision')
        if 'discount_id' in discount['discount']:
            assert isinstance(discount['discount'].pop('discount_id'), str)

        match_path = discount.get('match_path')
        if match_path:
            discount['match_path'].sort(
                key=lambda condition: condition['condition_name'],
            )
    discounts.sort(
        key=lambda discount: discount['discount'].get('description', ''),
    )
    return max_revision


def make_response_matched_results(match_results: List[dict]) -> None:
    match_results.sort(key=lambda result: result['hierarchy_name'])
    for result in match_results:
        make_response_matched_discounts(result['discounts'])


def make_match_discounts_response(
        response_json: dict, restoration_info_expected: bool,
) -> Optional[dict]:
    match_results = response_json['match_results']
    match_results.sort(key=lambda result: result['subquery_id'])
    for match_result in match_results:
        make_response_matched_results(match_result['results'])
    if restoration_info_expected:
        restoration_info = response_json.pop('restoration_info')
        restoration_info['versions'].sort(key=lambda version: version['name'])
        return restoration_info
    return None


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
            if not show_match_parameters and 'match_path' in discount:
                discount.pop('match_path')
    return match_results


def _prepare_match_discounts_expected_data(
        expected_data: dict,
        unique_hierarchy_names: Set[str],
        subqueries: List[dict],
        show_match_parameters: bool,
) -> None:
    for match_result in expected_data['match_results']:
        if not subqueries:
            match_result['subquery_id'] = 'no_subquery_id'
        match_result['results'] = make_expected_matched_results(
            match_result['results'],
            unique_hierarchy_names,
            show_match_parameters,
        )


def active_period_value(active_period: dict) -> dict:
    return {
        'condition_name': active_period['condition_name'],
        'value': active_period['values'][0],
    }


async def check_match_discounts(
        taxi_grocery_discounts,
        hierarchy_names: List[str],
        subqueries: List[dict],
        additional_common_conditions: Optional[dict],
        request_time: str,
        request_time_zone: str,
        show_match_parameters: bool,
        expected_data: dict,
        expected_status_code: int,
        additional_request_fields: Optional[dict] = None,
) -> Optional[dict]:
    expected_data = copy.deepcopy(expected_data)

    request: Dict[str, Any] = {
        'common_conditions': {
            'request_time': request_time,
            'request_timezone': request_time_zone,
        },
        'hierarchy_names': hierarchy_names,
        'subqueries': subqueries,
    }
    if additional_common_conditions is not None:
        request['common_conditions'].update(additional_common_conditions)
    if additional_request_fields is not None:
        request.update(additional_request_fields)

    response = await taxi_grocery_discounts.post(
        'v4/match-discounts/', request, headers=get_headers(),
    )

    assert response.status_code == expected_status_code
    if expected_status_code != 200:
        return None

    response_json = response.json()
    restoration_info = make_match_discounts_response(response_json, True)

    unique_hierarchy_names = set(hierarchy_names)
    _prepare_match_discounts_expected_data(
        expected_data,
        unique_hierarchy_names,
        subqueries,
        show_match_parameters,
    )
    assert response_json == expected_data
    return restoration_info


async def check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name: str,
        conditions: List[dict],
        limit: int,
        offset: Optional[int],
        expected_data: Optional[dict],
        expected_status_code: int,
        draft_ids: Optional[List[str]] = None,
        multidraft_ids: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
):
    def _make_expected_rules(
            expected_data: Optional[dict], hierarchy_name: str,
    ) -> Optional[dict]:
        if expected_data is None:
            return None
        result = {
            'discount_data': {
                'hierarchy_name': hierarchy_name,
                'discounts': expected_data[hierarchy_name],
            },
        }
        if hierarchy_name == 'cart_discounts':
            for discount in result['discount_data']['discounts']:
                discount['discount'].pop('product_set', None)
        return result

    expected_data = copy.deepcopy(expected_data)

    request = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'limit': limit,
        'draft_ids': draft_ids,
        'multidraft_ids': multidraft_ids,
        'authors': authors,
    }

    if offset is not None:
        request['offset'] = offset

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/search-rules/',
        request,
        headers=get_headers(),
    )

    assert response.status_code == expected_status_code

    response_json = response.json()
    if expected_status_code != 200:
        if expected_data is not None:
            assert response_json == expected_data
        return

    make_response_matched_discounts(
        response_json['discount_data']['discounts'],
    )
    expected_data = _make_expected_rules(expected_data, hierarchy_name)

    assert response_json == expected_data


def get_added_discount(
        add_rules_data: dict, hierarchy_name: str, add_index: int = 0,
) -> dict:
    discount = copy.deepcopy(
        add_rules_data[hierarchy_name][add_index]['discount'],
    )
    discount['active_with_surge'] = discount.get('active_with_surge', False)
    return discount


def get_matched_discount(
        add_rules_data: dict,
        hierarchy_name: str,
        matched_index: int = 0,
        add_index: int = 0,
) -> dict:
    discount = get_added_discount(add_rules_data, hierarchy_name, add_index)
    result: dict = {'active_with_surge': discount['active_with_surge']}

    max_set_apply_count = discount.get('max_set_apply_count')
    if max_set_apply_count is not None:
        result['max_set_apply_count'] = max_set_apply_count

    number_of_products = discount.get('number_of_products')
    if number_of_products is not None:
        result['number_of_products'] = number_of_products

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

    if hierarchy_name == 'cart_discounts':
        result['product_set'] = []
    return result


def cart_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'active_with_surge', 'value_type': 'Other'},
            {
                'condition_name': 'application_name',
                'value': 'some_application_name',
            },
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'class', 'value': 'No class'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'depot', 'value': 'some_depot'},
            {'condition_name': 'experiment', 'value_type': 'Other'},
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'orders_restriction', 'value_type': 'Other'},
            {'condition_name': 'product_set', 'value': []},
            {'condition_name': 'tag', 'value_type': 'Other'},
        ],
    }


def menu_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'class', 'value': 'No class'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'depot', 'value': 'some_depot'},
            {'condition_name': 'experiment', 'value_type': 'Other'},
            {'condition_name': 'group', 'value_type': 'Other'},
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'master_group', 'value_type': 'Other'},
            {'condition_name': 'orders_restriction', 'value_type': 'Other'},
            {'condition_name': 'product', 'value_type': 'Other'},
            {'condition_name': 'tag', 'value_type': 'Other'},
        ],
    }


def dynamic_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'label', 'value': 'some_label'},
        ],
    }


def markdown_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'depot', 'value': 'some_depot'},
            {'condition_name': 'master_group', 'value_type': 'Other'},
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'product', 'value_type': 'Other'},
            {'condition_name': 'tag', 'value_type': 'Other'},
        ],
    }


def suppliers_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'product', 'value_type': 'Other'},
        ],
    }


def payment_method_match_path(active_period: Optional[dict] = None) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    return {
        'match_path': [
            active_period_value(active_period),
            {
                'condition_name': 'application_name',
                'value': 'some_application_name',
            },
            {'condition_name': 'bins', 'value_type': 'Other'},
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'class', 'value': 'No class'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'depot', 'value': 'some_depot'},
            {'condition_name': 'experiment', 'value_type': 'Other'},
            {'condition_name': 'group', 'value_type': 'Other'},
            {'condition_name': 'has_yaplus', 'value_type': 'Other'},
            {'condition_name': 'master_group', 'value_type': 'Other'},
            {'condition_name': 'payment_method', 'value_type': 'Other'},
            {'condition_name': 'product', 'value_type': 'Other'},
        ],
    }


def get_match_path(
        hierarchy_name: str, active_period: Optional[dict] = None,
) -> dict:
    data: dict = {
        'cart_discounts': cart_match_path,
        'cart_cashback': cart_match_path,
        'menu_discounts': menu_match_path,
        'menu_cashback': menu_match_path,
        'bundle_discounts': menu_match_path,
        'bundle_cashback': menu_match_path,
        'payment_method_discounts': payment_method_match_path,
        'payment_method_cashback': payment_method_match_path,
        'dynamic_discounts': dynamic_match_path,
        'markdown_discounts': markdown_match_path,
        'suppliers_discounts': suppliers_match_path,
        'suppliers_cashback': suppliers_match_path,
    }
    if hierarchy_name in data:
        return data[hierarchy_name](active_period)
    raise Exception(f'Unsupported hierarhy {hierarchy_name}')


def get_add_rules_data(
        active_period: Optional[dict] = None,
        hierarchy_names: FrozenSet[str] = None,
        description: str = '1',
) -> dict:
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    rules_without_depot = [
        active_period,
        {'condition_name': 'city', 'values': ['213']},
        {'condition_name': 'country', 'values': ['some_country']},
    ]
    rules = rules_without_depot + [
        {'condition_name': 'depot', 'values': ['some_depot']},
    ]
    rules_with_application_name = rules + [
        {
            'condition_name': 'application_name',
            'values': ['some_application_name'],
        },
    ]
    rules_for_dynamic = [
        active_period,
        {'condition_name': 'label', 'values': ['some_label']},
    ]
    data = {
        'cart_discounts': (rules_with_application_name, small_cart_discount),
        'cart_cashback': (rules_with_application_name, small_cart_cashback),
        'menu_discounts': (rules, small_menu_discount),
        'menu_cashback': (rules, small_menu_cashback),
        'bundle_discounts': (rules, small_menu_discount),
        'bundle_cashback': (rules, small_menu_cashback),
        'payment_method_discounts': (
            rules_with_application_name,
            small_payment_method_discount,
        ),
        'payment_method_cashback': (
            rules_with_application_name,
            small_payment_method_cashback,
        ),
        'dynamic_discounts': (rules_for_dynamic, small_menu_discount),
        'markdown_discounts': (rules, small_markdown_discount),
        'suppliers_discounts': (rules_without_depot, small_suppliers_discount),
        'suppliers_cashback': (rules_without_depot, small_suppliers_cashback),
    }
    result = dict()
    for hierarchy_name in hierarchy_names or data.keys():
        rules, get_small_discount = data[hierarchy_name]
        result[hierarchy_name] = [
            {'rules': copy.deepcopy(rules), 'discount': get_small_discount()},
        ]
    return result


def get_full_add_rules_data(active_period: Optional[dict] = None):
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    rules = [
        active_period,
        {
            'condition_name': 'application_name',
            'values': ['some_application_name'],
        },
        {'condition_name': 'city', 'values': ['213']},
        {'condition_name': 'country', 'values': ['some_country']},
        {'condition_name': 'depot', 'values': ['some_depot']},
    ]
    return {
        'menu_discounts': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                'discount': {
                    'description': '1',
                    'active_with_surge': True,
                    'number_of_products': 11,
                    'discount_meta': {
                        'menu_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                        'is_expiring': False,
                        'is_price_strikethrough': True,
                    },
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
                            'cashback_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '10.0',
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
                    'description': '2',
                    'active_with_surge': False,
                    'max_set_apply_count': 10,
                    'discount_meta': {
                        'cart_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                    },
                    'product_set': [],
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
                            'cashback_value': {
                                'set_value': {
                                    'value_type': 'absolute',
                                    'value': '1.0',
                                },
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
                            'cashback_value': {
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
        'bundle_discounts': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                'discount': {
                    'description': '1',
                    'active_with_surge': True,
                    'number_of_products': 11,
                    'discount_meta': {
                        'menu_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                        'is_expiring': False,
                        'is_price_strikethrough': True,
                    },
                    'values_with_schedules': [
                        {
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
                    ],
                },
            },
        ],
        'payment_method_discounts': [
            {
                'rules': rules,
                'discount': {
                    'description': '3',
                    'active_with_surge': True,
                    'number_of_products': 18,
                    'discount_meta': {
                        'payment_method_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                    },
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
                                'cart_value': {
                                    'discount_values': {
                                        'value_type': 'table',
                                        'value': [
                                            {
                                                'from_cost': '11',
                                                'discount': {
                                                    'value_type': 'absolute',
                                                    'value': '6',
                                                },
                                            },
                                        ],
                                    },
                                    'maximum_discount': '5',
                                },
                            },
                            'cashback_value': {
                                'menu_value': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'from_cost': '10',
                                            'discount': {
                                                'value_type': 'absolute',
                                                'value': '5',
                                            },
                                        },
                                    ],
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
        'dynamic_discounts': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'label', 'values': ['some_label']},
                ],
                'discount': {
                    'description': '1',
                    'active_with_surge': True,
                    'number_of_products': 11,
                    'discount_meta': {
                        'menu_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                        'is_expiring': False,
                        'is_price_strikethrough': True,
                    },
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
                            'cashback_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '10.0',
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
        'markdown_discounts': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                'discount': {
                    'description': '1',
                    'active_with_surge': True,
                    'number_of_products': 11,
                    'discount_meta': {
                        'menu_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                        'is_expiring': False,
                        'is_price_strikethrough': True,
                    },
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
                            'cashback_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '10.0',
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
        'suppliers_discounts': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                ],
                'discount': {
                    'description': '1',
                    'discount_meta': {
                        'cart_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                    },
                    'values_with_schedules': [
                        {
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
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '15.0',
                                },
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
        'suppliers_cashback': [
            {
                'rules': [
                    active_period,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                ],
                'discount': {
                    'description': '1',
                    'discount_meta': {
                        'cart_discount': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'label_color': 'label_color',
                    },
                    'values_with_schedules': [
                        {
                            'cashback_value': {
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
                            'cashback_value': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '15.0',
                                },
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
    }


async def add_bin_set(
        taxi_grocery_discounts,
        request: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.post(
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
        taxi_grocery_discounts,
        data: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.post(
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


async def init_bin_sets(taxi_grocery_discounts) -> None:
    await add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'some_bins',
            'time': {
                'start': '2019-07-11T03:00:00',
                'end': '2021-07-18T03:00:00',
            },
            'bins': [123321, 2344321],
        },
    )
    await set_bin_sets_priority(
        taxi_grocery_discounts, {'bin_set_names': ['some_bins']},
    )


async def set_classes(
        taxi_grocery_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
) -> None:
    response = await taxi_grocery_discounts.post(
        CLASSES_URL,
        request,
        headers=get_draft_headers('draft_id_test_admin_classes'),
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json() == request
    elif expected_response is not None:
        assert response.json() == expected_response


async def init_classes(taxi_grocery_discounts) -> None:
    await set_classes(taxi_grocery_discounts, {'classes': ['No class']})


async def set_groups(
        taxi_grocery_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
) -> None:
    response = await taxi_grocery_discounts.post(
        GROUPS_URL,
        request,
        headers=get_draft_headers('draft_id_test_admin_groups'),
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json() == request
    elif expected_response is not None:
        assert response.json() == expected_response


async def init_groups(taxi_grocery_discounts, mocked_time) -> None:
    now = mocked_time.now()
    mocked_time.set(datetime.datetime(2019, 1, 1))
    await set_groups(
        taxi_grocery_discounts,
        {
            'groups_orders': [
                {'root_name': 'root1', 'groups': ['group2', 'group1']},
            ],
        },
    )
    mocked_time.set(datetime.datetime(2020, 1, 1))
    await set_groups(
        taxi_grocery_discounts,
        {
            'groups_orders': [
                {'root_name': 'root1', 'groups': ['group1', 'group2']},
                {'root_name': 'root2', 'groups': ['group3', 'group1']},
            ],
        },
    )
    mocked_time.set(datetime.datetime(2020, 1, 10))
    await set_groups(
        taxi_grocery_discounts,
        {
            'groups_orders': [
                {'root_name': 'root2', 'groups': ['group1', 'group3']},
            ],
        },
    )
    mocked_time.set(now)


class ListMixedObjects(list):
    """
    It is needed to check the sameness of two lists
    when the order of the elements is not important to us
    """

    def __eq__(self, other) -> bool:
        assert isinstance(other, (list, ListMixedObjects))
        copy_other = copy.deepcopy(other)
        try:
            for element in self:
                copy_other.remove(element)
            return not copy_other
        except ValueError:
            return False


class StartsWith:
    def __init__(self, string: str):
        self.string = string

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return other.startswith(self.string)
        if isinstance(other, StartsWith):
            return self.string == other.string
        return NotImplemented

    def __str__(self):
        return f'{self.string}...'

    def __repr__(self):
        return repr(str(self))
