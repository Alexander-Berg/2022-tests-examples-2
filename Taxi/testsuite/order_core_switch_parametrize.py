import pytest


PROTOCOL_SWITCH_TO_ORDER_CORE = pytest.mark.parametrize(
    'order_core_switch_on',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='protocol_switch_to_order_core',
                    consumers=['protocol/order-core-switch'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'handlers': [
                                    'changeporchnumber',
                                    'changecorpcostcenter',
                                    'changeaction',
                                    'changecomment',
                                    'changeclientgeosharing',
                                    'setdontcall',
                                    'setdontsms',
                                    'changepayment',
                                    'changedestinations',
                                    'totw',
                                    '/1.x/seen',
                                    'requestconfirm',
                                    'taxiroute',
                                ],
                            },
                        },
                    ],
                ),
            ],
        ),
    ],
)
