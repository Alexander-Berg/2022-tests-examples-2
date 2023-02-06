import pytest

from tests_cargo_crm import const


@pytest.mark.parametrize(
    ('get_active_status_response', 'should_notify'),
    (
        pytest.param(
            {
                'is_client_registration_finished': True,
                'is_contract_active': True,
            },
            False,
            id='registered client',
        ),
        pytest.param(
            {
                'is_client_registration_finished': False,
                'is_contract_active': True,
            },
            True,
            id='billing client, contract is active',
        ),
        pytest.param(
            {
                'is_client_registration_finished': False,
                'is_contract_active': False,
            },
            False,
            id='billing client, contract is not active',
        ),
    ),
)
async def test_stq_check_contract_is_active(
        stq_runner,
        mocked_cargo_corp,
        mocked_cargo_crm,
        get_active_status_response,
        should_notify,
):
    mocked_cargo_corp.contract_get_active_status.set_response(
        200, get_active_status_response,
    )
    mocked_cargo_crm.notification_contract_accepted.set_expected_data(
        {'corp_client_id': const.CORP_CLIENT_ID},
    )
    mocked_cargo_crm.notification_contract_accepted.set_response(200, {})

    await stq_runner.cargo_crm_check_contract_is_active.call(
        task_id=const.CORP_CLIENT_ID,
        kwargs={'corp_client_id': const.CORP_CLIENT_ID},
    )

    assert mocked_cargo_corp.contract_get_active_status_times_called == 1
    if should_notify:
        assert (
            mocked_cargo_crm.notification_contract_accepted_times_called == 1
        )
    else:
        assert (
            mocked_cargo_crm.notification_contract_accepted_times_called == 0
        )
