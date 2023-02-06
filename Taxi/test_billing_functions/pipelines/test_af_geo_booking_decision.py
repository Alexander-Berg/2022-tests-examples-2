import pytest

TEST_DOC_ID = 1234567890


@pytest.mark.now('2020-12-30T00:00:00.0Z')
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
async def test(
        stq_runner,
        do_mock_billing_docs,
        do_mock_billing_reports,
        reschedulable_stq_runner,
        load_json,
):
    docs = do_mock_billing_docs(
        [
            load_json('taxi_shift_pay.json'),
            load_json('af_decision_block.json'),
        ],
    )
    do_mock_billing_reports()
    queue = stq_runner.billing_functions_taxi_geo_booking_shift
    await reschedulable_stq_runner(queue, TEST_DOC_ID)

    assert docs.update_requests == load_json('updates.json')
