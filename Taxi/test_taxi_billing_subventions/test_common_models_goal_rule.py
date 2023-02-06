import typing as tp

import pytest

from taxi.billing import util

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'rule_json, balances_json, doc_json, expected_rule_event_handled_json',
    [
        (
            'goal_rule.json',
            'empty_balance_list.json',
            'moscow_doc.json',
            'moscow_rule_event_handled.json',
        ),
        (
            'goal_rule.json',
            'empty_balance_list.json',
            'subv_disable_all_doc.json',
            'unfit_subv_disable_all_rule_event_handled.json',
        ),
        (
            'goal_rule.json',
            'empty_balance_list.json',
            'short_doc.json',
            'moscow_rule_event_handled.json',
        ),
        (
            'goal_rule.json',
            'empty_balance_list.json',
            'spb_doc.json',
            'unfit_spb_rule_event_handled.json',
        ),
        (
            'sticker_rule.json',
            'empty_balance_list.json',
            'moscow_doc.json',
            'unfit_sticker_rule_event_handled.json',
        ),
        (
            'sticker_rule.json',
            'empty_balance_list.json',
            'sticker_doc.json',
            'sticker_rule_event_handled.json',
        ),
        (
            'two_days_goal_rule.json',
            'empty_balance_list.json',
            '10_may_moscow_doc.json',
            '10_may_moscow_rule_event_handled.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_on_order_ready_for_billing(
        rule_json,
        balances_json,
        doc_json,
        expected_rule_event_handled_json,
        load_py_json_dir,
):
    # pylint: disable=invalid-name
    rule: models.GoalRule
    doc_json: models.doc.OrderReadyForBilling
    expected_rule_event_handled: models.RuleEventHandled
    rule, balances, doc, expected_rule_event_handled = load_py_json_dir(
        'test_on_order_ready_for_billing',
        rule_json,
        balances_json,
        doc_json,
        expected_rule_event_handled_json,
    )
    actual_rule_event_handled = rule.on_order_ready_for_billing(
        doc,
        models.PaymentLevel.zero('RUB'),
        balances,
        driver_mode=models.DriverModeContext(None),
        log_extra=None,
    )
    assert actual_rule_event_handled == expected_rule_event_handled


@pytest.mark.parametrize(
    'rule_json, doc_json, expected_balances_json',
    [
        ('goal_rule.json', 'moscow_doc.json', 'expected_balances.json'),
        (
            'goal_rule.json',
            'moscow_2018_05_10_doc.json',
            'expected_2018_05_10_balances.json',
        ),
        (
            '7_days_goal_rule.json',
            'moscow_doc.json',
            'expected_7_days_balances.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_related_balance_queries(
        rule_json, doc_json, expected_balances_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    rule: models.GoalRule
    doc: models.doc.OrderReadyForBilling

    rule, doc, expected_balances = load_py_json_dir(
        'test_get_related_balance_queries',
        rule_json,
        doc_json,
        expected_balances_json,
    )
    entity_id = util.build_unique_driver_entity_id(
        str(doc.order.performer.unique_driver_id),
    )
    assert expected_balances == rule.get_related_balance_queries(
        entity_id, doc.order.due,
    )


@pytest.mark.parametrize(
    'rule_json, balances_json, expected_docs_json',
    [
        ('goal_rule.json', 'balances.json', 'expected_doc.json'),
        (
            'finite_max_num_orders_goal_rule.json',
            'finite_max_num_orders_balances.json',
            'expected_finite_max_num_orders_doc.json',
        ),
        (
            'finite_max_num_orders_goal_rule.json',
            'unfulfilled_finite_max_num_orders_balances.json',
            'expected_unfulfilled_finite_max_num_orders_doc.json',
        ),
        (
            'goal_rule.json',
            'unfulfilled_balances.json',
            'expected_unfulfilled_balances_doc.json',
        ),
        (
            'goal_rule.json',
            'empty_balances.json',
            'expected_empty_balances_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_goal_fulfilled(
        rule_json, balances_json, expected_docs_json, load_py_json_dir,
):
    rule: models.GoalRule
    expected_docs: tp.List[models.GoalFulfilled]
    rule, balances, expected_docs = load_py_json_dir(
        'test_get_goal_fulfilled',
        rule_json,
        balances_json,
        expected_docs_json,
    )
    actual_docs = rule.get_goal_fulfilled(balances)
    assert actual_docs == expected_docs
