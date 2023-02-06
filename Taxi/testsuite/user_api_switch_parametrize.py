import pytest


PROTOCOL_SWITCH_TO_USER_API = pytest.mark.parametrize(
    'user_api_switch_on',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    USER_API_USERS_ENDPOINTS={'users/get': True},
                ),
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='protocol_switch_to_user_api',
                    consumers=['protocol/user-api-switch'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'handlers': [
                                    'get-user-settings',
                                    'save-user-settings',
                                    'couponcheck',
                                    'email',
                                    'feedback',
                                    'cards',
                                ],
                            },
                        },
                    ],
                ),
            ],
        ),
    ],
)
