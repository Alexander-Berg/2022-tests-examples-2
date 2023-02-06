import pytest

from .. import consts

ORDERS_HISTORY_PERIOD = 24 * 30 * 3
ORDERS_HISTORY_LIMIT = 100

GROCERY_FALLBACK_PARAMS = {
    'service': 'grocery',
    'orders_history_period': ORDERS_HISTORY_PERIOD,
    'orders_history_limit': ORDERS_HISTORY_LIMIT,
}


class Configs:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.settings_grocery(
            orders_history_period=ORDERS_HISTORY_PERIOD,
            orders_history_limit=ORDERS_HISTORY_LIMIT,
        )
        self.originators(True)
        self.processing_name(None)

    def set_pass_payment_to_saturn(self, enabled):
        self.taxi_config.set(GROCERY_USER_DEBTS_PASS_PAYMENT_SATURN=enabled)

    def settings_grocery(
            self, *, orders_history_period, orders_history_limit=None,
    ):
        value = dict(
            service='grocery',
            orders_history_period=orders_history_period,
            orders_history_limit=orders_history_limit,
        )

        self.experiments3.add_config(
            name='grocery_user_debts_settings',
            consumers=['grocery-user-debts'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value={'predictor': {**value}},
        )

    def settings_saturn(
            self,
            *,
            grocery_fallback_params=None,
            saturn_formula_id=consts.SATURN_FORMULA_ID,
            saturn_service=consts.SATURN_SERVICE_RUSSIA,
            formula_threshold=consts.SATURN_FORMULA_THRESHOLD,
    ):
        default_value = {
            'predictor': {
                'service': 'saturn',
                'request_properties': {
                    'formula_id': saturn_formula_id,
                    'saturn_service': saturn_service,
                    'formula_threshold': formula_threshold,
                },
            },
        }

        if grocery_fallback_params is not None:
            default_value['fallback_predictor'] = {**grocery_fallback_params}

        self.experiments3.add_config(
            name='grocery_user_debts_settings',
            consumers=['grocery-user-debts'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=default_value,
        )

    def available_non_tech(
            self,
            *,
            orders_count_to_enable=0,
            debt_available=None,
            reason=None,
    ):
        if debt_available is not None:
            clause = {
                'title': 'Always',
                'predicate': {'init': {}, 'type': 'true'},
                'value': dict(enabled=debt_available, reason=reason),
            }
        else:
            clause = {
                'title': 'Filter by orders count',
                'predicate': {
                    'init': {
                        'arg_name': 'orders_count',
                        'arg_type': 'int',
                        'value': orders_count_to_enable,
                    },
                    'type': 'gte',
                },
                'value': dict(enabled=True),
            }

        self.experiments3.add_config(
            name='grocery_user_debts_available',
            consumers=['grocery-user-debts/available'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[clause],
            default_value=dict(enabled=False),
        )

    def available_tech(self, *, debt_available=False, reason=None):
        self.experiments3.add_config(
            name='grocery_user_debts_available_tech',
            consumers=['grocery-user-debts/available'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(enabled=debt_available, reason=reason),
        )

    def available_tech_by_error(self, **error_to_available):
        clauses = [
            {
                'title': 'Always',
                'predicate': {
                    'init': {
                        'arg_name': 'error_reason_code',
                        'arg_type': 'string',
                        'value': error,
                    },
                    'type': 'eq',
                },
                'value': dict(enabled=value),
            }
            for error, value in error_to_available.items()
        ]

        self.experiments3.add_config(
            name='grocery_user_debts_available_tech',
            consumers=['grocery-user-debts/available'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=clauses,
            default_value=dict(enabled=False),
        )

    def available(self, *, debt_available=False):
        self.available_tech(debt_available=debt_available)
        self.available_non_tech(debt_available=debt_available)

    def strategy(self, *, value=None):
        clause = {
            'title': 'Always',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'strategy': value},
        }

        self.experiments3.add_config(
            name='grocery_debts_strategy',
            consumers=['grocery-user-debts/strategy'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[clause],
            default_value=dict(strategy=value),
        )

    def originators(self, enabled=False):
        clause = {
            'title': 'Always',
            'predicate': {'init': {}, 'type': 'true'},
            'value': dict(enabled=enabled),
        }

        self.experiments3.add_config(
            name='grocery_user_debts_originators',
            consumers=['grocery-user-debts'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[clause],
        )

    def forgive(self, value: bool):
        self.experiments3.add_config(
            name='grocery_user_debts_forgive',
            consumers=['grocery-user-debts/strategy'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(enabled=value),
        )

    def error_reason_flow(self, flow: str):
        self.experiments3.add_config(
            name='grocery_user_debts_error_reason_flow',
            consumers=['grocery-user-debts'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(flow=flow),
        )

    def processing_name(self, name):
        self.experiments3.add_config(
            name='grocery_payments_processing_name',
            consumers=['grocery-user-debts'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(processing_name=name),
        )

    def grocery_user_debts_notify_user(self, enabled=True):
        self.experiments3.add_config(
            name='grocery_user_debts_notify_user',
            consumers=['grocery-user-debts/notify_user'],
            default_value=dict(enabled=enabled),
        )


@pytest.fixture(name='grocery_user_debts_configs', autouse=True)
def grocery_user_debts_configs(experiments3, taxi_config):
    return Configs(experiments3, taxi_config)
