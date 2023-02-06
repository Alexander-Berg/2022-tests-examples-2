# pylint: disable=too-many-lines
import copy
import random
from typing import List
from typing import Optional
from typing import Set


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


# Generated via `tvmknife unittest service -s 123 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIexCpEg:PkDHYmG'
    'PZmF01QRRlgate8JvdS2HrShQxHIsr9x3tuUSrcex'
    '_RkAId_QbiPURL8oSGUscDwFiDgBde0ZAFsj_Qq1h'
    'NnCSnAV_ygcAY2a_hoIIQzDhcUKtHgmS7x5YjTaog'
    'BHVF3ZC6lrWfqwmAxdGsavk_3ncMXJxDM25ygJK6Y'
)
SERVICE_NAME = 'ride_discounts'
PRIORITIZED_ENTITY_URL = '/v1/admin/prioritized-entity/'
PRIORITY_URL = '/v1/admin/priority/'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

ADD_RULES_URL = 'v1/admin/match-discounts/add-rules'
ADD_RULES_CHECK_URL = 'v1/admin/match-discounts/add-rules/check'

REDUCE_RULES_END_TIME_URL = 'v1/admin/match-discounts/reduce-rules-end-time'
REDUCE_RULES_END_TIME_CHECK_URL = (
    'v1/admin/match-discounts/reduce-rules-end-time/check'
)

DEFAULT_SCHEDULE = {
    'timezone': 'LOCAL',
    'intervals': [{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}],
}

VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T12:00:01+00:00',
            'is_start_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
            'is_end_utc': False,
        },
    ],
}

SERIES_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'


START_DATA_ID = '123'


def get_simple_discount_value() -> dict:
    return {
        'value_type': 'table',
        'value': [{'from_cost': 1.0, 'discount': 2.0}],
    }


def make_discount_value(
        discount_value: Optional[dict] = None,
        discounts_with_discount_counters: Optional[List[dict]] = None,
):
    if discount_value is None:
        discount_value = get_simple_discount_value()
    discount: dict = {'discount_value': discount_value}
    if discounts_with_discount_counters is not None:
        discount[
            'discounts_with_discount_counters'
        ] = discounts_with_discount_counters
    return discount


DEFAULT_MONEY_DISCOUNT = {
    'name': '1',
    'values_with_schedules': [
        {
            'money_value': make_discount_value(
                {'value_type': 'flat', 'value': 10.0},
            ),
            'schedule': DEFAULT_SCHEDULE,
        },
    ],
    'discount_meta': {
        'is_price_strikethrough': True,
        'branding_keys': {
            'default_branding_keys': {
                'card_title': 'some_title',
                'card_subtitle': 'some_subtitle',
                'payment_method_subtitle': 'some_payment_method_subtitle',
            },
            'combined_branding_keys': {
                'card_title': 'some_title',
                'card_subtitle': 'some_subtitle',
                'payment_method_subtitle': 'some_payment_method_subtitle',
            },
        },
    },
}

DEFAULT_CASHBACK_DISCOUNT = {
    'name': '1',
    'values_with_schedules': [
        {
            'cashback_value': make_discount_value(
                {'value_type': 'flat', 'value': 10.0},
            ),
            'schedule': DEFAULT_SCHEDULE,
        },
    ],
    'discount_meta': {
        'is_price_strikethrough': True,
        'branding_keys': {
            'default_branding_keys': {
                'card_title': 'some_title',
                'card_subtitle': 'some_subtitle',
                'payment_method_subtitle': 'some_payment_method_subtitle',
            },
            'combined_branding_keys': {
                'card_title': 'some_title',
                'card_subtitle': 'some_subtitle',
                'payment_method_subtitle': 'some_payment_method_subtitle',
            },
        },
    },
}


def get_headers():
    return {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


def get_draft_headers(draft_id: Optional[str] = None):
    return {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-YaTaxi-Draft-Author': 'user',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Tickets': 'ticket-1',
        'X-YaTaxi-Draft-Id': (draft_id or f'{SERVICE_NAME}_draft_id'),
    }


def get_max_revision(hierarchy_name: str, pgsql) -> int:
    pg_cursor = pgsql['ride_discounts'].cursor()
    pg_cursor.execute(
        f"""SELECT MAX(__revision)
            FROM ride_discounts.match_rules_{hierarchy_name};""",
    )
    return list(pg_cursor)[0][0]


def get_revision(pgsql) -> int:
    pg_cursor = pgsql['ride_discounts'].cursor()
    pg_cursor.execute(
        f"""SELECT last_value
            FROM ride_discounts.match_rules_revision;""",
    )
    return list(pg_cursor)[0][0]


def make_discount(
        name='1',
        additional_properties: Optional[dict] = None,
        hierarchy_name: str = 'full_money_discounts',
):
    if 'cashback' in hierarchy_name:
        result = copy.deepcopy(DEFAULT_CASHBACK_DISCOUNT)
    else:
        result = copy.deepcopy(DEFAULT_MONEY_DISCOUNT)
    result['name'] = name
    if additional_properties is not None:
        result.update(additional_properties)
    return result


async def add_prioritized_entity(
        client,
        request_body: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await client.post(
        PRIORITIZED_ENTITY_URL,
        request_body,
        headers=get_draft_headers('draft_id_test_admin_prioritized_entity'),
    )
    assert response.status_code == expected_status_code, response.json()
    response_json = response.json()
    if expected_status_code == 200:
        assert response_json == request_body
    elif expected_body is not None:
        assert response_json == expected_body


async def set_priority(
        client,
        request_body: dict,
        expected_body: Optional[dict] = None,
        expected_status_code: int = 200,
) -> None:
    response = await client.post(
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


async def check_find_rules(
        client,
        hierarchy_name: str,
        search_type: str,
        conditions: List[dict],
        expected_data: Optional[dict],
        expected_status_code: int,
):
    def _make_expected_rules(
            expected_data: Optional[dict], hierarchy_name: str,
    ) -> Optional[dict]:
        if expected_data is None:
            return None
        for discount in expected_data[hierarchy_name]:
            discount['match_path'].sort(
                key=lambda condition: condition['condition_name'],
            )
        return {
            'discount_data': {
                'hierarchy_name': hierarchy_name,
                'discounts': expected_data[hierarchy_name],
            },
        }

    def _make_response_matched_discounts(result: dict) -> int:
        """
        Returns maximal encountered revision or 0
        """
        max_revision = 0
        revision = result.pop('revision')
        assert isinstance(revision, int)
        if revision > max_revision:
            max_revision = revision
        result['match_path'].sort(
            key=lambda condition: condition['condition_name'],
        )
        _make_response_matched_discount(result)
        return max_revision

    def _make_response_matched_results(match_results: List[dict]) -> None:
        for result in match_results:
            _make_response_matched_discounts(result)

    def _prepare_response(response: Optional[dict]) -> Optional[dict]:
        if response and response['discount_data'].get('discounts'):
            for discount in response['discount_data']['discounts']:
                discount['meta_info'].pop('create_draft_id', None)
        return response

    expected_data = copy.deepcopy(expected_data)

    request = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'type': search_type,
    }

    response = await client.post(
        'v1/admin/match-discounts/find-rules/', request, headers=get_headers(),
    )

    assert response.status_code == expected_status_code

    response_json = response.json()

    if expected_status_code != 200:
        if expected_data is not None:
            assert response_json == expected_data
        return

    _make_response_matched_results(response_json['discount_data']['discounts'])

    expected_data = _make_expected_rules(expected_data, hierarchy_name)

    assert _prepare_response(response_json) == _prepare_response(expected_data)


def get_added_discount(
        add_rules_data: dict, hierarchy_name: str, add_index: int = 0,
) -> dict:
    discount = copy.deepcopy(
        add_rules_data[hierarchy_name][add_index]['discount'],
    )
    return discount


def get_experimental_match_path(active_period: dict, zone: dict) -> dict:
    return get_full_match_path(active_period, zone)


def get_full_match_path(active_period: dict, zone: dict) -> dict:
    return {
        'match_path': [
            active_period,
            {'condition_name': 'application_brand', 'value_type': 'Other'},
            {'condition_name': 'application_platform', 'value_type': 'Other'},
            {'condition_name': 'application_type', 'value_type': 'Other'},
            {'condition_name': 'class', 'value': 'default'},
            {'condition_name': 'geoarea_a_set', 'value': []},
            {'condition_name': 'geoarea_b_set', 'value': []},
            {'condition_name': 'has_yaplus', 'value': 1},
            {'condition_name': 'intermediate_point_is_set', 'value': 0},
            {'condition_name': 'order_type', 'value_type': 'Other'},
            {'condition_name': 'payment_method', 'value_type': 'Other'},
            {'condition_name': 'point_b_is_set', 'value': 1},
            {'condition_name': 'surge_range', 'value_type': 'Other'},
            {'condition_name': 'tag', 'value': 'some_tag'},
            {'condition_name': 'tag_from_experiment', 'value_type': 'Other'},
            {'condition_name': 'tariff', 'value': 'econom'},
            {'condition_name': 'zone', 'value': zone},
        ],
    }


def get_payment_method_match_path(active_period: dict, zone: dict) -> dict:
    return {
        'match_path': [
            active_period,
            {'condition_name': 'application_brand', 'value_type': 'Other'},
            {'condition_name': 'application_platform', 'value_type': 'Other'},
            {'condition_name': 'application_type', 'value_type': 'Other'},
            {'condition_name': 'bins', 'value': 'some_bins'},
            {'condition_name': 'has_yaplus', 'value': 1},
            {'condition_name': 'intermediate_point_is_set', 'value': 0},
            {'condition_name': 'order_type', 'value_type': 'Other'},
            {'condition_name': 'payment_method', 'value_type': 'Other'},
            {'condition_name': 'point_b_is_set', 'value_type': 'Other'},
            {'condition_name': 'tag', 'value': 'some_tag'},
            {'condition_name': 'tariff', 'value': 'econom'},
            {'condition_name': 'zone', 'value': zone},
        ],
    }


def get_add_rules_data(
        hierarchy_names: Set[str],
        active_period: Optional[dict] = None,
        name: str = '1',
        additional_discount_properties: Optional[dict] = None,
) -> dict:
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    common_rules = [
        active_period,
        {'condition_name': 'has_yaplus', 'values': [1]},
        {'condition_name': 'intermediate_point_is_set', 'values': [0]},
        {'condition_name': 'tag', 'values': ['some_tag']},
        {
            'condition_name': 'zone',
            'values': [
                {
                    'name': 'br_moscow',
                    'type': 'geonode',
                    'is_prioritized': False,
                },
            ],
        },
        {'condition_name': 'tariff', 'values': ['econom']},
    ]
    result = dict()
    for hierarchy_name in [
            'payment_method_money_discounts',
            'payment_method_cashback_discounts',
    ]:
        if hierarchy_name not in hierarchy_names:
            continue
        rules = copy.deepcopy(common_rules) + [
            {'condition_name': 'bins', 'values': ['some_bins']},
        ]
        result[hierarchy_name] = [
            {
                'rules': rules,
                'discount': make_discount(
                    name,
                    additional_discount_properties,
                    'payment_method_money_discounts',
                ),
            },
        ]
    for hierarchy_name in [
            'full_cashback_discounts',
            'experimental_cashback_discounts',
            'full_money_discounts',
            'experimental_money_discounts',
    ]:
        if hierarchy_name in hierarchy_names:
            rules = copy.deepcopy(common_rules) + [
                {'condition_name': 'point_b_is_set', 'values': [1]},
                {'condition_name': 'geoarea_a_set', 'values': [[]]},
                {'condition_name': 'geoarea_b_set', 'values': [[]]},
            ]
            result[hierarchy_name] = [
                {
                    'rules': rules,
                    'discount': make_discount(
                        name,
                        additional_discount_properties,
                        hierarchy_name=hierarchy_name,
                    ),
                },
            ]

    return result


def get_full_add_rules_data(active_period: Optional[dict] = None):
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD

    common_rules = [
        active_period,
        {'condition_name': 'has_yaplus', 'values': [1]},
        {'condition_name': 'intermediate_point_is_set', 'values': [0]},
        {'condition_name': 'tag', 'values': ['some_tag']},
        {
            'condition_name': 'zone',
            'values': [
                {
                    'name': 'br_moscow',
                    'type': 'geonode',
                    'is_prioritized': False,
                },
            ],
        },
        {'condition_name': 'tariff', 'values': ['econom']},
    ]
    return {
        'payment_method_money_discounts': [
            {
                'rules': copy.deepcopy(common_rules) + [
                    {'condition_name': 'bins', 'values': ['some_bins']},
                ],
                'discount': make_discount(
                    '3', hierarchy_name='payment_method_money_discounts',
                ),
            },
        ],
        'full_money_discounts': [
            {
                'rules': copy.deepcopy(common_rules) + [
                    {'condition_name': 'point_b_is_set', 'values': [1]},
                    {'condition_name': 'geoarea_a_set', 'values': [[]]},
                    {'condition_name': 'geoarea_b_set', 'values': [[]]},
                ],
                'discount': make_discount(
                    '4', hierarchy_name='full_money_discounts',
                ),
            },
        ],
        'experimental_money_discounts': [
            {
                'rules': copy.deepcopy(common_rules) + [
                    {'condition_name': 'point_b_is_set', 'values': [1]},
                    {'condition_name': 'geoarea_a_set', 'values': [[]]},
                    {'condition_name': 'geoarea_b_set', 'values': [[]]},
                ],
                'discount': make_discount(
                    '5', hierarchy_name='experimental_money_discounts',
                ),
            },
        ],
    }


HIERARCHY_NAMES = [
    'experimental_cashback_discounts',
    'experimental_money_discounts',
    'full_cashback_discounts',
    'full_money_discounts',
    'payment_method_cashback_discounts',
    'payment_method_money_discounts',
]
DEPRECATED_HIERARCHY_NAMES = [
    'full_discounts',
    'experimental_discounts',
    'payment_method_discounts',
]


def get_random_hierarchy_name():
    index = random.randint(0, len(HIERARCHY_NAMES) - 1)
    return HIERARCHY_NAMES[index]


def _make_response_matched_discount(result: dict):
    discount = result.get('discount')
    if discount:
        cashback_value = discount.get('cashback_value')
        if cashback_value:
            assert isinstance(cashback_value.pop('discount_id'), str)
            assert isinstance(cashback_value.pop('series_id'), str)
        money_value = discount.get('money_value')
        if money_value:
            assert isinstance(money_value.pop('discount_id'), str)
            assert isinstance(money_value.pop('series_id'), str)


def active_period_value(active_period: dict) -> dict:
    return {
        'condition_name': active_period['condition_name'],
        'value': active_period['values'][0],
    }


async def init_classes(client) -> None:
    await set_priority(
        client,
        {
            'prioritized_entity_type': 'class',
            'priority_groups': [
                {'name': 'default', 'entities_names': ['default']},
            ],
        },
    )


async def init_bin_sets(client) -> None:
    await add_prioritized_entity(
        client,
        {
            'name': 'some_bins',
            'data': {
                'active_period': {
                    'start': '2019-07-11T03:00:00',
                    'end': '2024-07-18T03:00:00',
                },
                'prioritized_entity_type': 'bin_set',
                'bins': ['600000', '600004'],
            },
        },
    )
    await set_priority(
        client,
        {
            'prioritized_entity_type': 'bin_set',
            'priority_groups': [
                {'name': 'default', 'entities_names': ['some_bins']},
            ],
        },
    )


async def load_discount(client, discount_id: str) -> Optional[dict]:
    response = await client.post(
        '/v1/admin/match-discounts/load-discount',
        headers=get_headers(),
        json={'discount_id': discount_id},
    )
    if response.status_code == 200:
        return response.json()
    return None
