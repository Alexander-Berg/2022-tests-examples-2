import typing as tp

import pytest

from taxi.billing import util

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'rule_json, doc_json, expected_output_doc_json',
    [
        ('rule.json', 'moscow_doc.json', 'moscow_journal_doc.json'),
        (
            'rule.json',
            'moscow_doc_with_none_modified_minimal_cost.json',
            'moscow_journal_doc.json',
        ),
        (
            'rule.json',
            'moscow_doc_with_modified_minimal_cost.json',
            'moscow_journal_doc.json',
        ),
        ('rule.json', 'spb_doc.json', 'unfit_spb_journal_doc.json'),
        ('rule.json', 'short_doc.json', 'unfit_short_journal_doc.json'),
        ('rule.json', 'mqc_doc.json', 'unfit_mqc_journal_doc.json'),
        ('cao_rule.json', 'zao_doc.json', 'unfit_zao_journal_doc.json'),
        ('tagged_rule.json', 'tagged_doc.json', 'tagged_journal_doc.json'),
        (
            'tagged_rule.json',
            'untagged_doc.json',
            'unfit_untagged_journal_doc.json',
        ),
        (
            'rule.json',
            'subv_disable_all_doc.json',
            'unfit_subv_disable_all_journal_doc.json',
        ),
        (
            '6_7_8_hour_rule.json',
            '9_hour_doc.json',
            'unfit_9_hour_journal_doc.json',
        ),
        (
            'friday_rule.json',
            'thursday_doc.json',
            'unfit_thursday_journal_doc.json',
        ),
        ('cash_rule.json', 'card_doc.json', 'unfit_card_journal_doc.json'),
        (
            'rule.json',
            'too_low_cost_doc.json',
            'unfit_too_low_cost_journal_doc.json',
        ),
        (
            'rule.json',
            'full_discount_low_cost_doc.json',
            'moscow_journal_doc.json',
        ),
        (
            'activity_rule.json',
            'moscow_doc.json',
            'unfit_too_low_activity_journal_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_on_order_ready_for_billing(
        rule_json, doc_json, expected_output_doc_json, load_py_json_dir,
):
    rule: models.SingleOrderRule
    doc: models.doc.OrderReadyForBilling
    expected_output_doc: models.RuleEventHandled
    rule, doc, expected_output_doc = load_py_json_dir(
        'test_on_order_ready_for_billing',
        rule_json,
        doc_json,
        expected_output_doc_json,
    )
    actual_output_doc = rule.on_order_ready_for_billing(
        doc,
        models.PaymentLevel.zero('RUB'),
        balances=[],
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
    rule: models.SingleOrderRule
    doc: models.doc.OrderReadyForBilling
    rule, doc = load_py_json_dir(
        'test_get_related_balance_queries', rule_json, doc_json,
    )
    entity_id = util.build_unique_driver_entity_id(
        str(doc.order.performer.unique_driver_id),
    )
    assert rule.get_related_balance_queries(entity_id, doc.order.due) == []


@pytest.mark.parametrize('rule_json', ['rule.json'])
@pytest.mark.nofilldb()
def test_get_goal_fulfilled(rule_json, load_py_json_dir):
    rule: models.SingleOrderRule
    rule = load_py_json_dir('test_get_goal_fulfilled', rule_json)
    assert models.GoalFulfilled(is_fulfilled=False) == rule.get_goal_fulfilled(
        [],
    )


@pytest.mark.parametrize(
    'rules_json, balances_json, doc_json, expected_output_doc_json',
    [
        (
            'one_rule.json',
            'balances.json',
            'moscow_doc.json',
            'moscow_journal_doc.json',
        ),
        (
            'greater_bonus_rules.json',
            'balances.json',
            'moscow_doc.json',
            'greater_bonus_journal_doc.json',
        ),
        (
            'same_bonus_rules.json',
            'balances.json',
            'moscow_doc.json',
            'same_bonus_journal_doc.json',
        ),
        (
            'rounding_error_rules.json',
            'balances.json',
            'rounding_error_doc.json',
            'rounding_error_journal_doc.json',
        ),
        (
            'greater_priority_rules.json',
            'balances.json',
            'moscow_doc.json',
            'greater_priority_journal_doc.json',
        ),
        (
            'one_additive_rules.json',
            'balances.json',
            'moscow_doc.json',
            'one_additive_journal_doc.json',
        ),
        (
            'empty_rules.json',
            'balances.json',
            'moscow_doc.json',
            'empty_journal_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_prioritized_on_order_ready_for_billing(
        rules_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
        load_py_json_dir,
):
    # pylint: disable=invalid-name
    rules: tp.List[models.SingleOrderRule]
    doc: models.doc.OrderReadyForBilling
    expected_output_doc: models.RuleEventHandled
    rules, balances, doc, expected_output_doc = load_py_json_dir(
        'test_prioritized_on_order_ready_for_billing',
        rules_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
    )
    actual_output_doc = models.handlers.on_order_ready_for_billing(
        rules,
        doc,
        balances,
        driver_mode=models.DriverModeContext(None),
        log_extra={},
    )
    assert expected_output_doc == actual_output_doc, repr(actual_output_doc)
