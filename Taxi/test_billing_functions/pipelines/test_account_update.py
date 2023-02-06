import pytest

from billing.docs import service as docs
from billing_models.generated import models
from taxi.billing.util import dates

from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._account_update import fetch_account_id
from billing_functions.stq.pipelines._account_update import update_account
from test_billing_functions import equatable

_MOCK_NOW = '2021-09-10T00:00:00.000000+00:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Results=pipeline.Results,
    Account=equatable.codegen(models.AccountUpdateAccount),
)
@pytest.mark.parametrize('test_data_json', ['fetch_account_id.json'])
async def test_fetch_account_id(
        test_data_json,
        stq3_context,
        load_json,
        load_py_json,
        do_mock_billing_accounts,
):
    test_data = load_py_json(test_data_json)

    raw_doc = test_data['doc']
    data = models.account_update.AccountUpdate.deserialize(raw_doc.data)
    account_update_doc = docs.TypedDoc.from_doc(raw_doc, data)

    do_mock_billing_accounts(
        existing_accounts=load_json('search_response.json'),
    )

    actual_results = await fetch_account_id.handle(
        stq3_context, account_update_doc,
    )
    assert actual_results == test_data['expected_results']


@pytest.mark.now(_MOCK_NOW)
@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Results=pipeline.Results,
    AccountsUpdate=equatable.codegen(models.AccountsUpdateResponse),
    Update=equatable.codegen(models.AccountUpdateExpired),
)
@pytest.mark.parametrize('test_data_json', ['update_account.json'])
async def test_update_account(
        test_data_json, stq3_context, load_py_json, do_mock_billing_accounts,
):
    test_data = load_py_json(test_data_json)

    raw_doc = test_data['doc']
    data = models.account_update.AccountUpdate.deserialize(raw_doc.data)
    account_update_doc = docs.TypedDoc.from_doc(raw_doc, data)

    do_mock_billing_accounts()

    actual_results = await update_account.handle(
        stq3_context, account_update_doc,
    )
    assert actual_results == test_data['expected_results']


@pytest.mark.now(_MOCK_NOW)
@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Results=pipeline.Results,
    Account=models.AccountUpdateAccount,
)
async def test_process_doc(
        do_mock_billing_accounts,
        do_mock_billing_docs,
        do_mock_billing_reports,
        stq_runner,
        reschedulable_stq_runner,
        load_json,
):
    process_docs = do_mock_billing_docs([load_json('doc_create.json')])
    do_mock_billing_accounts(
        existing_accounts=load_json('search_response.json'),
    )
    do_mock_billing_reports()

    task = stq_runner.billing_functions_account_update
    await reschedulable_stq_runner(task, 123456)

    expected_response = load_json('process_doc_response.json')
    assert process_docs.update_requests == expected_response
