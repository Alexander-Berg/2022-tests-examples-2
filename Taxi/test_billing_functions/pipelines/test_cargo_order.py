import pytest

TEST_DOC_ID = 1234567890


@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'coupon/paid': 137,
        'commission/card': 128,
        'cash': 111,
    },
    PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00',
    BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new',
)
@pytest.mark.parametrize(
    'test_data_path', ['cargo_order_with_claims.json', 'cargo_order.json'],
)
@pytest.mark.now('2020-12-30T00:00:00.0Z')
async def test_process_document(
        test_data_path,
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_replication,
        mock_billing_subventions_x,
        reschedulable_stq_runner,
        mock_tlog,
        mock_limits,
        load_json,
):
    docs = do_mock_billing_docs([load_json(test_data_path)])
    mock_replication(load_json('contracts.json'))
    mock_billing_subventions_x(**load_json('subvention_rules.json'))
    do_mock_billing_reports()
    do_mock_billing_accounts(
        existing_entities=load_json('entities.json'),
        existing_accounts=load_json('accounts.json'),
    )
    task = stq_runner.billing_functions_cargo_order
    await reschedulable_stq_runner(task, TEST_DOC_ID)
    assert docs.update_requests == load_json('updates.json')
