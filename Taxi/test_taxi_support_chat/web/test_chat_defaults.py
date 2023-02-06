import json

import pytest


@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
)
@pytest.mark.parametrize(
    ['payload', 'expected_result'],
    [
        (
            {'owner': {'id': '5b2cae5cb2682a976914c2a3', 'role': 'client'}},
            {'actions': [], 'view': {'show_message_input': True}},
        ),
        (
            {
                'owner': {
                    'id': '5b2cae5cb2682a976914c2a3',
                    'role': 'sms_client',
                },
            },
            {'actions': [], 'view': {'show_message_input': True}},
        ),
    ],
)
async def test_defaults(
        web_app_client,
        patch_support_scenarios_matcher,
        payload,
        expected_result,
):
    patch_support_scenarios_matcher()
    response = await web_app_client.post(
        '/v1/chat/defaults/', data=json.dumps(payload),
    )
    assert response.status == 200
    assert await response.json() == expected_result
