import datetime

import asynctest
import pytest

from billing.accounts import service as _accounts
from testsuite.utils import ordered_object

from billing_functions.functions import forward_tlog_entries


@pytest.mark.json_obj_hook(
    Query=forward_tlog_entries.Query, SelectedEntry=_accounts.SelectedEntry,
)
@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
@pytest.mark.config(
    BILLING_FUNCTIONS_SEND_ENTRIES_TO_BILLING_FIN_PAYOUTS=True,
    BILLING_FUNCTIONS_TOPICS_FOR_FIN_PAYOUTS_STQ=['topic'],
)
# pylint: disable=invalid-name
async def test_process_entries(
        test_data_json='test_data.json',
        *,
        make_context,
        mock_tlog,
        patched_stq_queue,
        load_py_json,
):
    test_data = load_py_json(test_data_json)

    context = make_context(test_data['entries'])
    await forward_tlog_entries.execute(context, test_data['query'])
    assert mock_tlog.journal_v1 == test_data['expected_tlog_v1_requests']
    assert mock_tlog.journal_v2 == test_data['expected_tlog_v2_requests']
    ordered_object.assert_eq(
        patched_stq_queue.pop_calls(),
        test_data['expected_stq_calls'],
        ['', 'task_id'],
    )


@pytest.fixture(name='make_context')
def make_make_context(stq3_context):
    def _make_context(entries):
        stq3_context.journal = asynctest.Mock(spec=_accounts.Journal)
        stq3_context.journal.select_by_id_or_die.return_value = entries
        stq3_context.journal.max_age_for_new_entries = datetime.timedelta(92)
        return stq3_context

    return _make_context
