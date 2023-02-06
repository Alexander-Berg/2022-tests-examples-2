import pytest


CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP = pytest.mark.parametrize(
    'order_core_exp_enabled',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='create_order_draft_in_order_core',
                    consumers=['protocol/createdraft'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': False},
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='create_order_draft_in_order_core',
                    consumers=['protocol/createdraft'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': True},
                        },
                    ],
                ),
            ],
        ),
    ],
)
