import decimal
import itertools
import typing as tp

import pytest

from taxi import billing

from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.models import handlers


@pytest.mark.parametrize(
    'rules_json, balances_json, doc_json, expected_output_doc_json',
    [
        (
            'rules.json',
            'balances.json',
            'moscow_doc.json',
            'moscow_rule_event_handled.json',
        ),
        (
            'dg_rules.json',
            'balances.json',
            'moscow_doc.json',
            'moscow_dg_rule_event_handled.json',
        ),
        (
            'dg_rules.json',
            'balances.json',
            'moscow_doc_with_tag.json',
            'moscow_dg_with_tag_rule_event_handled.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_on_order_ready_for_billing(
        rules_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
        load_py_json_dir,
):
    rules, balances, doc, expected_output_doc = load_py_json_dir(
        'test_on_order_ready_for_billing',
        rules_json,
        balances_json,
        doc_json,
        expected_output_doc_json,
    )
    actual_output_doc = handlers.on_order_ready_for_billing_additive(
        rules=rules,
        doc=doc,
        balances_by_id=balances,
        driver_mode=models.DriverModeContext(None),
        log_extra={},
    )
    assert expected_output_doc == actual_output_doc


@pytest.mark.parametrize(
    'rules_json, doc_json, expected_online_time',
    [('rules.json', 'doc.json', 7), ('rules1.json', 'doc1.json', 3.05)],
)
def test_on_driver_geoarea_activity(
        db, rules_json, doc_json, expected_online_time, load_py_json_dir,
):
    rules: tp.List[models.GeoBookingRule]
    doc: models.doc.DriverGeoareaActivity
    rules, doc = load_py_json_dir(
        'test_on_driver_geoarea_activity', rules_json, doc_json,
    )
    event_handled = handlers.on_driver_geoarea_activity(
        rules=rules, doc=doc, driver_mode=models.DriverModeContext(None),
    )
    entries = list(
        itertools.chain.from_iterable(
            [handled.journal.journal_entries for handled in event_handled],
        ),
    )
    journal_doc = models.doc.SubventionJournal(entries)
    expected = billing.Money(
        decimal.Decimal(str(expected_online_time)), billing.Money.NO_CURRENCY,
    )
    assert expected == journal_doc.get_sub_accounts_sum(
        ['time/free_minutes'], billing.Money.NO_CURRENCY,
    )
