import pytest

from taxi_billing_subventions import process_doc
from test_taxi_billing_subventions import helpers


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_discount_with_limit_order_completed_creates_orfb(
        stq_process_doc_context,
        mock_billing_docs,
        mock_subventions,
        load_json,
):
    doc = load_json('order_completed.json')
    docs = mock_billing_docs(doc)
    await process_doc.stq_task.task(
        stq_process_doc_context,
        task_info=helpers.create_task_info(),
        doc_id=doc['doc_id'],
    )
    _assert_doc(load_json('order_ready_for_billing.json'), docs.created_docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_discount_with_limit_orfb_creates_af_check(
        stq_process_doc_context,
        mock_parks_replica,
        mock_billing_docs,
        mock_billing_accounts,
        mock_billing_replication,
        mock_subventions,
        load_json,
):
    doc = load_json('order_ready_for_billing.json')
    docs = mock_billing_docs(doc)
    mock_billing_accounts()
    _enable_antifraud(stq_process_doc_context.config)
    await process_doc.stq_task.task(
        stq_process_doc_context,
        task_info=helpers.create_task_info(),
        doc_id=doc['doc_id'],
        log_extra={'_link': 'a_link'},
    )
    _assert_doc(
        load_json('subvention_antifraud_check.json'), docs.created_docs,
    )


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_discount_with_limit_af_check_creates_payouts(
        stq_process_doc_context,
        mock_billing_docs,
        mock_antifraud,
        mock_billing_orders,
        mock_subventions,
        load_json,
):
    doc = load_json('subvention_antifraud_check.json')
    mock_billing_docs(doc, load_json('order_ready_for_billing.json'))
    mock_antifraud(load_json('antifraud_pay.json'))
    orders = mock_billing_orders()
    _enable_antifraud(stq_process_doc_context.config)
    await process_doc.stq_task.task(
        stq_process_doc_context,
        task_info=helpers.create_task_info(),
        doc_id=doc['doc_id'],
    )
    _assert_orders(load_json('payout_subvention.json'), orders.events)


def _enable_antifraud(cfg):
    setattr(cfg, 'BILLING_SUBVENTIONS_PROCEDURE_INSTANT_SUBVENTION', True)
    setattr(
        cfg,
        'PAYOUT_MIGRATION',
        {
            'subventions': {
                'enabled': {'__default__': [{'first_date': '2020-01-01'}]},
            },
        },
    )


def _assert_doc(expected, actual_docs):
    expected.pop('doc_id', None)
    assert expected['kind'] in [d['kind'] for d in actual_docs], (
        'Doc %s was not created' % expected
    )
    for actual in actual_docs:
        if actual['kind'] == expected['kind']:
            assert actual == expected


def _assert_orders(expected, actual_docs):
    for orders in actual_docs:
        for actual in orders['orders']:
            if expected['kind'] == actual['kind']:
                assert expected == actual


@pytest.fixture(name='mock_subventions')
def make_mock_subventions(mockserver):
    @mockserver.json_handler('/billing-subventions/v1/process_doc')
    @staticmethod
    def _mock(_):
        return {}

    return _mock
