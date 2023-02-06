import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


@pytest.mark.config(
    AGENT_PAYDAY_SETTINGS={
        'default_percent': 58,
        'enable': True,
        'org_uid': '',
    },
    AGENT_ACTIVATE_EXPORT_PAYDAY_USER_BALANCE=True,
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'call-taxi-unified': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
        'call-taxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_directsupport',
        },
    },
)
@pytest.mark.parametrize(
    'expected_payday_requests',
    [
        pytest.param(
            [
                {
                    'employeeId': 'calltaxi_support',
                    'balance': {
                        'balance': '23.22',
                        'balanceFrom': '01.02.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_wrong_status',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '01.02.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_too_much_money',
                    'balance': {
                        'balance': '100000',
                        'balanceFrom': '01.02.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'directsupport_support',
                    'balance': {
                        'balance': '35.98',
                        'balanceFrom': '01.02.2021 00:00:00',
                    },
                },
            ],
            marks=[pytest.mark.now('2021-02-01T10:00:00')],
        ),
        pytest.param(
            [
                {
                    'employeeId': 'calltaxi_support',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '01.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_wrong_status',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '01.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_too_much_money',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '01.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'directsupport_support',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '01.01.2021 00:00:00',
                    },
                },
            ],
            marks=[pytest.mark.now('2021-01-15T10:00:00')],
        ),
        pytest.param(
            [
                {
                    'employeeId': 'calltaxi_support',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '16.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_wrong_status',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '16.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'calltaxi_support_too_much_money',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '16.01.2021 00:00:00',
                    },
                },
                {
                    'employeeId': 'directsupport_support',
                    'balance': {
                        'balance': '0.0',
                        'balanceFrom': '16.01.2021 00:00:00',
                    },
                },
            ],
            marks=[pytest.mark.now('2021-01-31T10:00:00')],
        ),
    ],
)
async def test_export_payday_user_balance(
        cron_context: context.Context,
        mock_payday_piecework_load,
        mock_payday_employee_balance,
        expected_payday_requests,
):
    await run_cron.main(
        ['agent.crontasks.export_payday_user_balance', '-t', '0'],
    )

    payday_requests = []
    while mock_payday_employee_balance.has_calls:
        payday_requests.append(
            mock_payday_employee_balance.next_call()['request'].json,
        )

    assert expected_payday_requests == payday_requests
