import pytest


RETRY_AFTER_SECONDS = pytest.mark.experiments3(
    name='grocery_payments_tracking_status_retry_interval',
    is_config=True,
    consumers=['grocery-payments-tracking/status-retry-interval'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'interval 1',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'seconds_lifetime',
                                'value': 20000,
                                'arg_type': 'int',
                            },
                            'type': 'lt',
                        },
                        {
                            'init': {
                                'arg_name': 'payment_type',
                                'value': 'cibus',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'retry-interval': 1},
        },
        {
            'title': 'default interval 10',
            'predicate': {'type': 'true'},
            'value': {'retry-interval': 10},
        },
    ],
    default_value={'retry-interval': 10},
)


def set_payment_tracking_enabled(experiments3, enabled):
    experiments3.add_config(
        name='grocery_orders_payment_tracking_enabled',
        consumers=['grocery-payments-tracking'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )
