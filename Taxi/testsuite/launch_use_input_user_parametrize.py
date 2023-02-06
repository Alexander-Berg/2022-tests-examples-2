import pytest


LAUNCH_USE_INPUT_FIELDS = pytest.mark.parametrize(
    'use_input_fields',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='protocol_launch_use_input_user',
                    consumers=['client_protocol/launch_preauth'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'user': [
                                    'authorized',
                                    'device_id',
                                    'phone_id',
                                    'yandex_uid',
                                    'yandex_uuid',
                                    'has_ya_plus',
                                    'has_cashback_plus',
                                ],
                                'phone': [],
                                'enabledLogDiff': True,
                            },
                        },
                    ],
                ),
            ],
        ),
    ],
)
