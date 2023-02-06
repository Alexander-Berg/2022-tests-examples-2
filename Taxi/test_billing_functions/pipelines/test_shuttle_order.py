import pytest

TEST_DOC_ID = 1234567890
TEST_DOC_ID_V2 = 1234567891


@pytest.mark.now('2020-12-30T00:00:00.0Z')
@pytest.mark.config(BILLING_SUBVENTIONS_SHIFT_OPEN_MAX_REQUEST_AGE_HRS=48)
async def test_process_document(
        stq_runner,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_replication,
        mock_billing_subventions_x,
        mock_open_shift,
        reschedulable_stq_runner,
        load_json,
):
    docs = do_mock_billing_docs(
        [load_json('shuttle_order.json'), load_json('subscriptions.json')],
    )
    do_mock_billing_reports()
    do_mock_billing_accounts(
        existing_entities=load_json('entities.json'),
        existing_accounts=load_json('accounts.json'),
    )
    mock_replication(load_json('contracts.json'))
    mock_billing_subventions_x(**load_json('subvention_rules.json'))

    task = stq_runner.billing_functions_shuttle_order
    await reschedulable_stq_runner(task, TEST_DOC_ID)

    assert docs.update_requests == load_json('updates.json')


@pytest.fixture(name='mock_open_shift')
def _mock_open_shift(mockserver):
    requests = []

    @mockserver.json_handler('/billing_subventions/v1/shifts/open')
    def _rules_select(request):
        requests.append(request.json)
        return {'doc_id': 666666}

    return requests
