import typing as tp

import pytest

from taxi.billing import util

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'rule_json, balances_json, doc_json, expected_output_doc_json',
    [
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'moscow_doc.json',
            'moscow_rule_event_handled.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'spb_doc.json',
            'unfit_spb_rule_event_handled.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'subv_disable_all_doc.json',
            'unfit_subv_disable_all_rule_event_handled.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'corp_doc_without_vat.json',
            'corp_rule_event_handled_without_vat.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'moscow_doc_cancelled.json',
            'moscow_rule_event_handled_cancelled.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'cost_for_driver_doc.json',
            'cost_for_driver_rule_event.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'call_center_doc.json',
            'call_center_rule_event.json',
        ),
        (
            'net_daily_guarantee_rule.json',
            'empty_balance_list.json',
            'call_center_doc.json',
            'call_center_net_rule_event.json',
        ),
        (
            'daily_guarantee_rule.json',
            'empty_balance_list.json',
            'call_center_with_cost_for_driver_doc.json',
            'call_center_with_cost_for_driver_rule_event.json',
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
    rule: models.DailyGuaranteeRule
    doc_json: models.doc.OrderReadyForBilling
    expected_output_doc: models.RuleEventHandled
    rule, balances, doc, expected_output_doc = load_py_json_dir(
        'test_on_order_ready_for_billing',
        rule_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
    )
    actual_output_doc = _rule_event_handled(
        rule.on_order_ready_for_billing(
            doc,
            models.PaymentLevel.zero('RUB'),
            balances,
            driver_mode=models.DriverModeContext(None),
            log_extra=None,
        ),
    )
    assert expected_output_doc == actual_output_doc


def _rule_event_handled(
        dg_reh: models.DgRuleEventHandled,
) -> models.RuleEventHandled:
    return models.RuleEventHandled(
        journal=dg_reh.journal,
        shift_ended_events=dg_reh.shift_ended_events,
        full_subvention_details=dg_reh.full_subvention_details,
        taxi_shifts=[],
    )


@pytest.mark.parametrize(
    'rule_json, doc_json, expected_balances_json',
    [
        (
            'daily_guarantee_rule.json',
            'moscow_doc.json',
            'expected_balances.json',
        ),
        (
            'daily_guarantee_rule_net.json',
            'moscow_doc.json',
            'expected_balances_net.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_related_balance_queries(
        rule_json, doc_json, expected_balances_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    rule: models.DailyGuaranteeRule
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
        ('daily_guarantee_rule.json', 'balances.json', 'expected_docs.json'),
        (
            'daily_guarantee_rule.json',
            'empty_balances.json',
            'expected_empty_docs.json',
        ),
        (
            'net_daily_guarantee_rule.json',
            'net_balances.json',
            'expected_net_docs.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_goal_fulfilled(
        rule_json, balances_json, expected_docs_json, load_py_json_dir,
):
    rule: models.DailyGuaranteeRule
    expected_docs: tp.List[models.GoalFulfilled]
    rule, balances, expected_docs = load_py_json_dir(
        'test_get_goal_fulfilled',
        rule_json,
        balances_json,
        expected_docs_json,
    )
    actual_docs = rule.get_goal_fulfilled(balances)
    assert actual_docs == expected_docs


@pytest.mark.parametrize(
    'rule_json, balances_json, expected_rule_id_json',
    [
        ('rule.json', 'balances.json', 'rule_id_for_details.json'),
        ('rule.json', 'empty_balances.json', 'empty_rule_id_for_details.json'),
    ],
)
@pytest.mark.nofilldb()
def test_get_rule_id_for_details(
        rule_json, balances_json, expected_rule_id_json, load_py_json_dir,
):
    rule: models.DailyGuaranteeRule
    expected_rule_id_json: models.rule.Identity
    rule, balances, expected_rule_id = load_py_json_dir(
        'test_get_rule_id_for_details',
        rule_json,
        balances_json,
        expected_rule_id_json,
    )
    goal_fulfilled = rule.get_goal_fulfilled(balances)
    assert rule.get_rule_id_for_details(goal_fulfilled) == expected_rule_id
