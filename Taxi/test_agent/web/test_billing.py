import pytest

from agent.internal import billing


@pytest.mark.parametrize(
    'login,coins_balance',
    [('webalex', 220), ('mikh-vasily', 120), ('liambaev', 0)],
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'wallet': 'calltaxi',
        },
    },
)
async def test_billing(
        web_app_client,
        web_context,
        mock_billing_balance,
        login,
        coins_balance,
):
    result = await billing.balance(
        context=web_context, login=login, project='calltaxi',
    )
    assert result == coins_balance
