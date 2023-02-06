import pytest


PROTOCOL_SWITCH_TO_REPLICA_DBUSERS = pytest.mark.parametrize(
    'read_from_replica_dbusers',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='protocol_switch_to_replica_dbusers',
                    consumers=['protocol/replica_dbusers_switch'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'handlers': [
                                    'changepayment',
                                    'clientgeo',
                                    'feedback',
                                    'integration_suggest',
                                    'orderbase',
                                    'ordercommit',
                                    'ordercontactobtain',
                                    'orderdraft',
                                    'ordersestimate',
                                    'orderssearch',
                                    'reorder',
                                    'sharedroute',
                                    'totw',
                                    'user_device_fingerprint',
                                ],
                            },
                        },
                    ],
                ),
            ],
        ),
    ],
)
