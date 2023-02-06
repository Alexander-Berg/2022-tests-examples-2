import pytest

TEST_DOC_ID = 1234567890
TEST_DOC_ID_AF = 1234567892


@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'coupon/paid': 137,
        'commission/card': 128,
        'cash': 111,
    },
    DRIVER_PROMOCODES_MIN_COMMISSION={'__default__': 1},
    PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00',
    BILLING_FUNCTIONS_CREATE_COMMISSION_SUPPORT_INFO_DOC=True,
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='old',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='both',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new',
            ),
        ),
    ],
)
@pytest.mark.now('2020-12-30T00:00:00.0Z')
async def test_process_document(
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_replication,
        mock_billing_commissions,
        mock_billing_subventions_x,
        mock_driver_work_modes,
        reschedulable_stq_runner,
        mock_tlog,
        mock_limits,
        load_json,
):
    docs = do_mock_billing_docs(
        [
            load_json('cargo_claim.json'),
            load_json('af_cargo_claim_decision.json'),
        ],
    )
    mock_billing_commissions(
        agreements=load_json('commission_agreements.json'),
    )
    mock_replication(load_json('contracts.json'))
    mock_driver_work_modes('dwm_responses.json')
    mock_billing_subventions_x(**load_json('subvention_rules.json'))
    do_mock_billing_reports()
    do_mock_billing_accounts(
        existing_entities=load_json('entities.json'),
        existing_accounts=load_json('accounts.json'),
    )
    task = stq_runner.billing_functions_cargo_claim
    await reschedulable_stq_runner(task, TEST_DOC_ID)
    await reschedulable_stq_runner(task, TEST_DOC_ID_AF)
    assert docs.update_requests == load_json('updates.json')
