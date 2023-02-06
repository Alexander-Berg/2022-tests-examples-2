import collections
import datetime

import pytest

from taxi_billing_subventions import process_doc
from test_taxi_billing_subventions import helpers


MOCK_NOW = '2020-07-01T17:30:45Z'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'completed_json,orfb_json',
    (
        ('order_completed.json', 'order_ready_for_billing.json'),
        ('order_completed_cargo.json', 'orfb_cargo.json'),
    ),
)
async def test_smart_goal_order_completed_creates_orfb(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_subventions,
        stq_client_patched,
        load_json,
        completed_json,
        orfb_json,
):
    doc = load_json(completed_json)
    docs = mock_billing_docs(doc)
    mock_billing_accounts()
    mock_billing_subventions()
    await _process_doc(stq_process_doc_context, doc)
    assert docs.create.times_called == 1
    _assert_doc(load_json(orfb_json), docs.created_docs)


@pytest.mark.now(MOCK_NOW)
async def test_smart_goal_orfb_gets_matching_rules_from_bsx(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_replication,
        matches,
        mock_parks_replica,
        stq_client_patched,
        load_json,
        patched_discovery,
):
    doc = load_json('order_ready_for_billing.json')
    mock_billing_accounts()
    mock_billing_docs(doc)
    _enable_order_ready_for_billing_configs(stq_process_doc_context.config)
    await _process_doc(stq_process_doc_context, doc)
    assert matches.matcher.times_called == 1
    assert matches.matcher.next_call()['request'].json == load_json(
        'expected_bsx_request.json',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'orfb_json', ('order_ready_for_billing.json', 'orfb_cargo.json'),
)
async def test_smart_goal_orfb_creates_accounts(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_replication,
        mock_parks_replica,
        stq_client_patched,
        load_json,
        patched_discovery,
        orfb_json,
):
    doc = load_json(orfb_json)
    mock_billing_docs(doc)
    accs = mock_billing_accounts()
    _enable_order_ready_for_billing_configs(stq_process_doc_context.config)
    await _process_doc(stq_process_doc_context, doc)
    assert accs.v1_accounts_create.times_called == 2
    assert accs.created_accounts == load_json('expected_accounts.json')


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'orfb_json,expected_doc_json',
    (
        ('order_ready_for_billing.json', 'subvention_journal.json'),
        ('order_ready_for_billing.json', 'taxi_shift.json'),
        ('orfb_cargo.json', 'subvention_journal_cargo.json'),
        ('orfb_cargo.json', 'taxi_shift_cargo.json'),
    ),
)
async def test_smart_goal_orfb_creates_docs(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_replication,
        mock_parks_replica,
        stq_client_patched,
        patch,
        load_json,
        patched_discovery,
        orfb_json,
        expected_doc_json,
):
    doc = load_json(orfb_json)
    docs = mock_billing_docs(doc)
    mock_billing_accounts()
    _enable_order_ready_for_billing_configs(stq_process_doc_context.config)
    await _process_doc(stq_process_doc_context, doc)
    assert docs.create.times_called == 2
    _assert_doc(load_json(expected_doc_json), docs.created_docs)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'orfb_json,expected_eta',
    (
        ('order_ready_for_billing.json', '2020-07-06T01:53:28.000000+00:00'),
        ('orfb_cargo.json', '2020-07-06T03:53:28.000000+00:00'),
    ),
)
async def test_smart_goal_orfb_schedules_taxi_shift_processing(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_replication,
        matches,
        mock_parks_replica,
        stq_client_patched,
        patch,
        load_json,
        patched_discovery,
        orfb_json,
        expected_eta,
):
    doc = load_json(orfb_json)
    mock_billing_docs(doc)
    mock_billing_accounts()
    _enable_order_ready_for_billing_configs(stq_process_doc_context.config)
    setattr(
        stq_process_doc_context.config,
        'BILLING_SUBVENTIONS_LOGISTICS_SHIFT_DELAY',
        6 * 60 * 60,
    )
    await _process_doc(stq_process_doc_context, doc)
    assert stq_client_patched.calls == [
        {
            'queue': matches.queue,
            'eta': datetime.datetime.fromisoformat(expected_eta),
            'task_id': 'doc_id/5001',
            'args': (5001,),
            'kwargs': None,
        },
    ]


@pytest.mark.now(MOCK_NOW)
async def test_smart_goal_orfb_cancelled_by_status(
        stq_process_doc_context,
        mock_billing_accounts,
        mock_billing_docs,
        mock_billing_replication,
        mock_parks_replica,
        load_json,
        patched_discovery,
):
    doc = load_json('order_ready_for_billing.json')
    doc['data']['order'].update({'taxi_status': 'cancelled'})
    docs = mock_billing_docs(doc)
    mock_billing_accounts()
    _enable_order_ready_for_billing_configs(stq_process_doc_context.config)
    await _process_doc(stq_process_doc_context, doc)
    assert docs.create.times_called == 1
    _assert_doc(
        load_json('subvention_journal_unmatched.json'), docs.created_docs,
    )


@pytest.fixture(
    name='matches',
    autouse=True,
    params=[
        ('bsx_matches.json', 'billing_functions_taxi_goal_shift'),
        (
            'bsx_matches_personal.json',
            'billing_functions_taxi_personal_goal_shift',
        ),
    ],
    ids=['goal', 'personal_goal'],
)
def _matches(mock_billing_subventions_x, request):
    Matcher = collections.namedtuple('Matcher', 'matcher,queue')
    return Matcher(
        matcher=mock_billing_subventions_x(request.param[0]),
        queue=request.param[1],
    )


async def _process_doc(context, doc):
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )


def _assert_doc(expected, actual_docs):
    expected.pop('doc_id', None)
    assert expected['kind'] in [d['kind'] for d in actual_docs], (
        'Doc %s was not created' % expected
    )
    for actual in actual_docs:
        if actual['kind'] == expected['kind']:
            assert expected == actual


def _enable_order_ready_for_billing_configs(cfg):
    setattr(cfg, 'BILLING_SUBVENTIONS_ENABLE_SMART_GOALS', True)
    setattr(cfg, 'CONVERT_UNFIT_TO_SUPPORT_INFO', True)
