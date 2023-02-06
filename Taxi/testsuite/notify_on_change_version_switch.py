import pytest


NOTIFY_ON_CHANGE_VERSION_SWITCH = pytest.mark.parametrize(
    'notify_on_change_version_switch',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='notify_on_change_version_switch',
                    consumers=['protocol/order-core-switch'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'switch': [
                                    'changeporchnumber',
                                    'setdontcall',
                                    'changeclientgeosharing',
                                    'changeaction',
                                    'changecomment',
                                ],
                                'disable': [
                                    'changecorpcostcenter',
                                    'setdontsms',
                                ],
                            },
                        },
                    ],
                ),
            ],
        ),
    ],
)
