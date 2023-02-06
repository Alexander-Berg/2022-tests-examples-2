import pytest

from billing.accounts import _billing_accounts
import billing.docs.service as docs_service
from taxi.billing.util import dates

from billing_functions.functions.core import tags
from billing_functions.repositories import journal
from billing_functions.repositories import migration_mode


@pytest.mark.json_obj_hook(
    CreateEntryRequest=journal.CreateEntryRequest,
    AppendedEntry=journal.AppendedEntry,
    Doc=docs_service.Doc,
)
@pytest.mark.parametrize(
    'test_data_json',
    ('append_to_new_doc.json', 'append_to_existing_doc.json'),
)
@pytest.mark.now('2021-06-18T00:00:00+00:00')
async def test_docs_repository_append(
        test_data_json, *, load_py_json, mock_billing_components,
):
    test_data = load_py_json(test_data_json)
    components = mock_billing_components(now=dates.utc_now_with_tz())
    if 'existing_doc' in test_data:
        components.docs.items.append(test_data['existing_doc'])

    repo = journal.DocsRepository(
        components.journal,
        components.accounts,
        components.docs,
        'alias_id',
        'taxi_order_journal',
        [tags.for_billing_docs_in_admin('alias_id')],
    )
    entries = await repo.append(test_data['request'])
    assert len(components.docs.items) == 1
    assert test_data['expected_doc'] == components.docs.items[0]
    assert test_data['expected_result'] == entries


@pytest.mark.parametrize(
    'test_data_json', ('restore_and_load_by_ids.json', 'load_by_ids.json'),
)
@pytest.mark.json_obj_hook(
    CreateEntryRequest=journal.CreateEntryRequest,
    Account=journal.Account,
    SelectedEntry=journal.SelectedEntry,
    Doc=docs_service.Doc,
)
@pytest.mark.now('2021-06-18T00-00:00+00:00')
async def test_doc_will_be_restored(
        do_mock_billing_docs,
        do_mock_billing_reports,
        do_mock_billing_accounts,
        load_json,
        load_py_json,
        stq3_context,
        *,
        test_data_json,
):
    test_data = load_py_json(test_data_json)
    do_mock_billing_reports(test_data['existing_reports_docs'])
    do_mock_billing_docs(test_data['existing_docs_docs'])
    do_mock_billing_accounts(existing_accounts=load_json('accounts.json'))
    repo = journal.DocsRepository(
        stq3_context.journal,
        stq3_context.accounts,
        stq3_context.docs,
        'alias_id',
        'taxi_order_journal',
        [tags.for_billing_docs_in_admin('alias_id')],
    )
    entries = await repo.select_by_id(test_data['request'])
    assert entries == test_data['expected_result']


@pytest.mark.parametrize(
    'repository_type, mode',
    (
        (journal.LogOnlyRepository, migration_mode.Mode.DISABLED),
        (journal.DocsRepository, migration_mode.Mode.TEST),
        (_billing_accounts.BillingJournal, migration_mode.Mode.ENABLED),
    ),
)
async def test_make(repository_type, mode, stq3_context):
    repo = journal.make(
        stq3_context, mode, 'alias_id', 'taxi_order_journal', [],
    )
    assert isinstance(repo, repository_type)
