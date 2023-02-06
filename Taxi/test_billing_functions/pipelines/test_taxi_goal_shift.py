import pytest

TEST_DOC_ID = 1234567890
TEST_DOC_ID_V2 = 1234567891


@pytest.mark.config(
    BILLING_COUNTRIES_WITH_ORDER_BILLINGS_SUBVENTION_NETTING={
        'rus': '2020-07-05',
    },
    BILLING_TLOG_SERVICE_IDS={'subvention/netted': 111},
    SUBVENTION_ANTIFRAUD_NEEDED_STARTUP_WINDOW=2,
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
async def test_taxi_shift_smart_goal_updates_taxi_shift(
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_antifraud,
        mock_driver_work_modes,
        reschedulable_stq_runner,
        mock_tlog,
        mock_limits,
        load_json,
):
    docs = do_mock_billing_docs(
        [load_json('taxi_shift.json'), load_json('taxi_shift_v2.json')],
    )
    do_mock_billing_accounts(
        existing_balances=load_json('balances.json'),
        existing_entities=load_json('entities.json'),
        existing_accounts=load_json('accounts.json'),
        existing_entries=load_json('entries.json'),
    )
    mock_antifraud(
        [
            # for v1
            load_json('antifraud_delay_response.json'),
            load_json('antifraud_pay_response.json'),
            # for v2
            load_json('antifraud_delay_response.json'),
            load_json('antifraud_pay_response.json'),
        ],
    )
    mock_driver_work_modes('dwm_responses.json')
    do_mock_billing_reports()

    queue = stq_runner.billing_functions_taxi_goal_shift
    await reschedulable_stq_runner(queue, TEST_DOC_ID)
    await reschedulable_stq_runner(queue, TEST_DOC_ID_V2)

    assert docs.update_requests == load_json('updates.json')
