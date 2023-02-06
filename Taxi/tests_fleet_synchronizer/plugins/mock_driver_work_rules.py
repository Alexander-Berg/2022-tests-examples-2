import copy

import pytest


WORK_RULE = {
    'commission_for_driver_fix_percent': '0.0000',
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': '45345',
    'type': 'park',
}

CALC_TABLE = [
    {
        'commission_fixed': '0.0000',
        'commission_percent': '0.0000',
        'is_enabled': False,
        'order_type_id': '8111ea73aeed482d820f4e87d20e9028',
    },
    {
        'commission_fixed': '1.0000',
        'commission_percent': '11.0000',
        'is_enabled': True,
        'order_type_id': 'af0efd4b0fa9e111a6fc00304879209b',
    },
    {
        'commission_fixed': '1.0000',
        'commission_percent': '111.0000',
        'is_enabled': True,
        'order_type_id': 'random_other_order_type',
    },
]

ORDER_TYPES_DATA = {
    'order_types': [
        {
            'id': '8111ea73aeed482d820f4e87d20e9028',
            'autocancel_time_in_seconds': 10,
            'driver_cancel_cost': '50.0000',
            'color': 'White',
            'morning_visibility': {'period': 'м', 'value': 3},
            'name': 'Name',
            'night_visibility': {'period': 'скрыть', 'value': -1},
            'is_client_address_shown': True,
            'is_client_phone_shown': True,
            'driver_waiting_cost': '50.0000',
            'weekend_visibility': {'period': '', 'value': 0},
        },
        {
            'id': 'af0efd4b0fa9e111a6fc00304879209b',
            'autocancel_time_in_seconds': 10,
            'driver_cancel_cost': '50.0000',
            'color': 'White',
            'morning_visibility': {'period': 'м', 'value': 3},
            'name': 'Yandex',
            'night_visibility': {'period': 'скрыть', 'value': -1},
            'is_client_address_shown': True,
            'is_client_phone_shown': True,
            'driver_waiting_cost': '50.0000',
            'weekend_visibility': {'period': '', 'value': 0},
        },
        {
            'id': 'random_other_order_type',
            'autocancel_time_in_seconds': 10,
            'driver_cancel_cost': '50.0000',
            'color': 'White',
            'morning_visibility': {'period': 'м', 'value': 3},
            'name': 'Random',
            'night_visibility': {'period': 'скрыть', 'value': -1},
            'is_client_address_shown': True,
            'is_client_phone_shown': True,
            'driver_waiting_cost': '50.0000',
            'weekend_visibility': {'period': '', 'value': 0},
        },
    ],
}


def _rule(num: int, ext: bool) -> dict:
    return {
        'id': f'rule_{num}',
        **WORK_RULE,
        **({'calc_table': CALC_TABLE} if ext else {}),
    }


def _num_from_id(rule_id: str) -> int:
    return int(rule_id[rule_id.find('_') + 1 :])


class DriverWorkRulesContext:
    def __init__(self):
        self.work_rules = {}
        self.mock_order_types_list = None
        self.mock_order_types_put = None
        self.mock_list_rules = None
        self.mock_get_extended_rule = None
        self.mock_put_extended_rule = None

    def set_rules(self, park_id, ids_int):
        if park_id not in self.work_rules:
            self.work_rules[park_id] = {}

        for num in ids_int:
            self.work_rules[park_id][f'rule_{num}'] = _rule(num, True)

    def get_rules(self, park_id):
        return [
            copy.deepcopy(rule) for rule in self.work_rules[park_id].values()
        ]


@pytest.fixture(name='driver_work_rules')
def dwr_fixture(mockserver):
    context = DriverWorkRulesContext()

    @mockserver.json_handler('/driver-work-rules/sync/v1/order-types/list')
    async def _mock_order_types_list(request):
        assert request.method == 'POST'
        return ORDER_TYPES_DATA

    @mockserver.json_handler('/driver-work-rules/sync/v1/order-types')
    async def _mock_order_types_put(request):
        assert request.method == 'PUT'
        assert request.json == ORDER_TYPES_DATA
        return ORDER_TYPES_DATA

    @mockserver.json_handler('/driver-work-rules/v1/work-rules/list')
    async def _mock_list_rules(request):
        assert request.method == 'POST'
        park_id = request.json['query']['park']['id']

        return {
            'work_rules': [
                rule for rule in context.work_rules.get(park_id, {}).values()
            ],
        }

    @mockserver.json_handler('/driver-work-rules/v1/work-rules')
    async def _mock_get_extended_rule(request):
        assert request.method == 'GET'
        return _rule(_num_from_id(request.query['id']), True)

    @mockserver.json_handler('/driver-work-rules/sync/v1/work-rules')
    async def _mock_put_extended_rule(request):
        assert request.method == 'PUT'
        park_id = request.query['park_id']
        rule = request.json['work_rule']

        if park_id not in context.work_rules:
            context.work_rules[park_id] = []

        context.work_rules[park_id][rule['id']] = rule
        return rule

    context.mock_order_types_list = _mock_order_types_list
    context.mock_order_types_put = _mock_order_types_put
    context.mock_list_rules = _mock_list_rules
    context.mock_get_extended_rule = _mock_get_extended_rule
    context.mock_put_extended_rule = _mock_put_extended_rule

    return context
