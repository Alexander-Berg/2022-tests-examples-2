from __future__ import annotations

import pytest

from taxi_billing_subventions import process_doc
from test_taxi_billing_subventions import helpers


@pytest.mark.now('2020-09-01T21:00:00')
async def test_single_ride_v2_antifraud_check_calls_antifraud(
        stq_process_doc_context,
        mock_antifraud,
        mock_billing_docs,
        mock_billing_orders,
        load_json,
        stq_client_patched,
):
    antifraud = mock_antifraud(load_json('antifraud_pay.json'))
    mock_billing_docs(
        load_json('subvention_calculation.json'),
        load_json('subvention_antifraud_check.json'),
    )
    mock_billing_orders()
    await _run_antifraud_check(stq_process_doc_context, load_json)
    assert antifraud.times_called == 1
    expected = load_json('antifraud_request.json')
    assert antifraud.next_call()['request'].json == expected


@pytest.mark.now('2020-09-01T21:00:00')
@pytest.mark.parametrize(
    'calc_doc_json,antifraud_response_json,orders_request_json',
    (
        (
            'subvention_calculation.json',
            'antifraud_pay.json',
            'orders_pay.json',
        ),
        (
            'subvention_calculation.json',
            'antifraud_delay.json',
            'orders_delay.json',
        ),
        (
            'subvention_calculation.json',
            'antifraud_block.json',
            'orders_block.json',
        ),
        (
            'subvention_calculation_after_delay.json',
            'antifraud_pay.json',
            'orders_pay_after_delay.json',
        ),
        (
            'subvention_calculation_after_delay.json',
            'antifraud_delay.json',
            None,
        ),
        (
            'subvention_calculation_after_delay.json',
            'antifraud_block.json',
            'orders_block_after_delay.json',
        ),
    ),
)
async def test_single_ride_v2_antifraud_check_calls_orders(
        stq_process_doc_context,
        load_json,
        mock_antifraud,
        mock_billing_docs,
        mock_billing_orders,
        mock_billing_subventions,
        stq_client_patched,
        calc_doc_json,
        antifraud_response_json,
        orders_request_json,
):
    mock_antifraud(load_json(antifraud_response_json))
    mock_billing_docs(
        load_json(calc_doc_json), load_json('subvention_antifraud_check.json'),
    )
    mock_billing_subventions()
    orders = mock_billing_orders()
    await _run_antifraud_check(stq_process_doc_context, load_json)
    if orders_request_json is not None:
        expected = load_json(orders_request_json)
        assert orders.events == [expected]
    else:
        assert orders.v2_process_async.times_called == 0


@pytest.mark.now('2020-09-01T21:00:00')
@pytest.mark.parametrize(
    'calc_data_json,antifraud_response_json,expected',
    (
        (
            'subvention_calculation.json',
            'antifraud_pay.json',
            'docs_update_pay.json',
        ),
        (
            'subvention_calculation.json',
            'antifraud_delay.json',
            'docs_update_delay.json',
        ),
        (
            'subvention_calculation_after_delay.json',
            'antifraud_pay.json',
            'docs_update_pay_after_delay.json',
        ),
        (
            'subvention_calculation_after_delay.json',
            'antifraud_delay.json',
            None,
        ),
    ),
)
async def test_single_ride_v2_antifraud_check_update_calc_data(
        stq_process_doc_context,
        load_json,
        mock_antifraud,
        mock_billing_docs,
        mock_billing_orders,
        mock_billing_subventions,
        stq_client_patched,
        calc_data_json,
        antifraud_response_json,
        expected,
):
    mock_antifraud(load_json(antifraud_response_json))
    docs = mock_billing_docs(
        load_json(calc_data_json),
        load_json('subvention_antifraud_check.json'),
    )
    mock_billing_subventions()
    mock_billing_orders()
    await _run_antifraud_check(stq_process_doc_context, load_json)
    if expected is not None:
        assert docs.update.times_called == 1
        actual = docs.update.next_call()['request'].json
        assert actual == load_json(expected)
    else:
        assert docs.update.times_called == 0


@pytest.mark.now('2020-09-01T21:00:00')
@pytest.mark.parametrize(
    'calc_doc_json',
    (
        (
            'subvention_calculation.json',
            'subvention_calculation_after_delay.json',
        )
    ),
)
async def test_single_ride_subventions_v2_create_new_task_when_delay(
        stq_process_doc_context,
        patch,
        mock_antifraud,
        mock_billing_docs,
        mock_billing_orders,
        mock_billing_subventions,
        load_json,
        calc_doc_json,
):
    @patch('random.randint')
    def _randint(*_args, **_kwargs):
        return 1111

    mock_antifraud(load_json('antifraud_delay.json'))
    docs = mock_billing_docs(
        load_json(calc_doc_json), load_json('subvention_antifraud_check.json'),
    )
    mock_billing_orders()
    subventions = mock_billing_subventions()
    await _run_antifraud_check(stq_process_doc_context, load_json)
    assert docs.create.times_called == 1
    assert docs.created_docs == [
        load_json('subvention_antifraud_check_after_delay.json'),
    ]
    assert subventions.process_doc.times_called == 1
    assert subventions.scheduled_docs == [load_json('process_doc.json')]


@pytest.mark.now('2020-09-01T21:00:00')
@pytest.mark.parametrize(
    'antifraud_response_json,expected_calls,expected_ids',
    (
        ('antifraud_pay.json', 2, [1212, 2222]),
        ('antifraud_delay.json', 1, [2222]),
        ('antifraud_block.json', 2, [1212, 2222]),
    ),
)
async def test_single_ride_v2_antifraud_check_completes_calc_doc(
        stq_process_doc_context,
        load_json,
        load_py_json,
        mock_antifraud,
        mock_billing_docs,
        mock_billing_orders,
        mock_billing_subventions,
        stq_client_patched,
        antifraud_response_json,
        expected_calls,
        expected_ids,
):
    mock_antifraud(load_json(antifraud_response_json))
    docs = mock_billing_docs(
        load_json('subvention_calculation.json'),
        load_json('subvention_antifraud_check.json'),
    )
    mock_billing_orders()
    mock_billing_subventions()
    await _run_antifraud_check(stq_process_doc_context, load_json)
    assert docs.finish_processing.times_called == expected_calls
    assert docs.finished_docs == expected_ids


async def _run_antifraud_check(context, load_json):
    setattr(
        context.config,
        'BILLING_SUBVENTIONS_PROCEDURE_INSTANT_SUBVENTION',
        True,
    )
    doc = load_json('subvention_antifraud_check.json')
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )


@pytest.mark.now('2020-10-01T21:00:00')
@pytest.mark.parametrize(
    'decision_doc_json,calc_doc_json,orders_json',
    (
        (
            'antifraud_changed_decision_to_pay.json',
            'subvention_calculation.json',
            'orders_pay.json',
        ),
        (
            'antifraud_changed_decision_to_block.json',
            'subvention_calculation.json',
            'orders_block.json',
        ),
        (
            'antifraud_changed_decision_to_pay.json',
            'subvention_calculation_after_delay.json',
            None,
        ),
        (
            'antifraud_changed_decision_to_block.json',
            'subvention_calculation_after_delay.json',
            None,
        ),
        (
            'antifraud_changed_decision_to_block.json',
            'subvention_calculation_after_pay.json',
            'orders_block.json',
        ),
        (
            'antifraud_changed_decision_to_pay.json',
            'subvention_calculation_after_block.json',
            'orders_pay.json',
        ),
    ),
)
async def test_single_ride_v2_sends_payouts_when_af_changed_decision(
        stq_process_doc_context,
        mock_billing_docs,
        mock_billing_orders,
        load_json,
        decision_doc_json,
        calc_doc_json,
        orders_json,
):
    doc = load_json(decision_doc_json)
    mock_billing_docs(doc, load_json(calc_doc_json))
    orders = mock_billing_orders()
    await _run_antifraud_action(stq_process_doc_context, doc)
    if orders_json is not None:
        expected = load_json(orders_json)
        assert orders.events == [expected]
    else:
        assert orders.v2_process_async.times_called == 0


@pytest.mark.now('2020-10-01T21:00:00')
@pytest.mark.parametrize(
    'decision_doc_json,calc_doc_json,followup_doc_json',
    (
        (
            'antifraud_changed_decision_to_pay.json',
            'subvention_calculation_after_block.json',
            'subvention_calculation_followup_pay.json',
        ),
        (
            'antifraud_changed_decision_to_block.json',
            'subvention_calculation_after_pay.json',
            'subvention_calculation_followup_block.json',
        ),
    ),
)
async def test_single_ride_v2_creates_doc_with_history_for_changed_decision(
        stq_process_doc_context,
        mock_billing_docs,
        mock_billing_orders,
        load_json,
        decision_doc_json,
        calc_doc_json,
        followup_doc_json,
):
    doc = load_json(decision_doc_json)
    docs = mock_billing_docs(doc, load_json(calc_doc_json))
    mock_billing_orders()
    await _run_antifraud_action(stq_process_doc_context, doc)
    expected = load_json(followup_doc_json)
    assert docs.created_docs == [expected]


async def _run_antifraud_action(context, doc):
    setattr(context.config, 'BILLING_SUBVENTIONS_PROCESS_AF_ACTION', True)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
