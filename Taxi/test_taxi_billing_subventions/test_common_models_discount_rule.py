import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'rule_json, balances_json, doc_json, expected_output_doc_json',
    [
        (
            'rule.json',
            'empty_balance_list.json',
            'moscow_doc.json',
            'moscow_journal_doc.json',
        ),
        (
            'rule.json',
            'empty_balance_list.json',
            'moscow_subv_disable_all_doc.json',
            'moscow_journal_doc.json',
        ),
        (
            'rule.json',
            'empty_balance_list.json',
            'moscow_completed_by_dispatcher_doc.json',
            'moscow_completed_by_dispatcher_journal_doc.json',
        ),
        (
            'rule.json',
            'empty_balance_list.json',
            'moscow_mqc_doc.json',
            'moscow_mqc_journal_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_on_order_ready_for_billing(
        rule_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
        load_py_json_dir,
):
    rule, balances, doc, expected_output_doc = load_py_json_dir(
        'test_on_order_ready_for_billing',
        rule_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
    )
    actual_output_doc = rule.on_order_ready_for_billing(
        doc,
        models.PaymentLevel.zero('RUB'),
        balances,
        driver_mode=models.DriverModeContext(None),
        log_extra=None,
    )
    assert expected_output_doc == actual_output_doc


@pytest.mark.parametrize(
    'rule_json, doc_json', [('rule.json', 'moscow_doc.json')],
)
@pytest.mark.nofilldb()
def test_get_related_balance_queries(rule_json, doc_json, load_py_json_dir):
    # pylint: disable=invalid-name
    rule, doc = load_py_json_dir(
        'test_get_related_balance_queries', rule_json, doc_json,
    )
    assert rule.get_related_balance_queries('entity_id', doc.order.due) == []


@pytest.mark.parametrize('rule_json', ['rule.json'])
@pytest.mark.nofilldb()
def test_get_goal_fulfilled(rule_json, load_py_json_dir):
    rule: models.SingleOrderRule
    rule = load_py_json_dir('test_get_goal_fulfilled', rule_json)
    assert models.GoalFulfilled(is_fulfilled=False) == rule.get_goal_fulfilled(
        [],
    )
