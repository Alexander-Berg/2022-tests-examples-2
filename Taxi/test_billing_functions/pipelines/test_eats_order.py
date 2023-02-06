import pytest

TEST_DOC_ID = 1234567890


@pytest.mark.skip(reason='temporary disabled')
@pytest.mark.now('2020-12-30T00:00:00.0Z')
async def test_process_document(
        stq_runner,
        do_mock_billing_docs,
        reschedulable_stq_runner,
        do_mock_billing_reports,
        load_json,
):
    docs = do_mock_billing_docs([load_json('eats_order.json')])
    do_mock_billing_reports()
    task = stq_runner.billing_functions_eats_order
    await reschedulable_stq_runner(task, TEST_DOC_ID)
    assert docs.update_requests == load_json('updates.json')
