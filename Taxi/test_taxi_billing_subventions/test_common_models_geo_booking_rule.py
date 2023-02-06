import typing as tp

import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'test_data_json, rule_json, driver_mode_tags',
    [
        ('fit_whole_interval.json', 'rule.json', []),
        ('fit_partial_interval_1.json', 'rule.json', []),
        ('fit_partial_interval_2.json', 'rule.json', []),
        ('unfit_activity.json', 'rule.json', []),
        ('unfit_activity.json', 'rule_with_inverted_relaxation.json', []),
        ('unfit_tags.json', 'rule.json', []),
        ('unfit_subv_disable_all_tag.json', 'rule.json', []),
        ('unfit_tags.json', 'rule_with_inverted_relaxation.json', []),
        ('unfit_profile_payment_type_restrictions.json', 'rule.json', []),
        (
            'unfit_profile_payment_type_restrictions.json',
            'rule_with_inverted_relaxation.json',
            [],
        ),
        ('unfit_tariff_classes.json', 'rule.json', []),
        (
            'unfit_tariff_classes.json',
            'rule_with_inverted_relaxation.json',
            [],
        ),
    ],
)
def test_on_driver_geoarea_activity(
        test_data_json, rule_json, load_py_json_dir, driver_mode_tags,
):
    rule = load_py_json_dir('test_on_driver_geoarea_activity', rule_json)
    test_data: dict = load_py_json_dir(
        'test_on_driver_geoarea_activity', test_data_json,
    )
    expected_event_handled = test_data['expected_event_handled']
    event = test_data['event']
    actual_event_handled = rule.on_driver_geoarea_activity(
        doc=models.doc.DriverGeoareaActivity(
            unique_driver_id='111111111111111111111111',
            clid='clid',
            db_id='db_id',
            driver_uuid='uuid',
            time_interval=event.interval,
            geoarea_activities=[event],
            activity_points=test_data['activity_points'],
            tags=frozenset(test_data['tags']),
            available_tariff_classes=test_data['available_tariff_classes'],
            profile_payment_type_restrictions=(
                test_data['profile_payment_type_restrictions']
            ),
            rule_types=[],
        ),
        driver_mode=models.DriverModeContext(None),
        log_extra=None,
    )
    assert actual_event_handled == expected_event_handled


@pytest.mark.parametrize(
    'test_data_json',
    [
        'fit_all.json',
        'unfit_zone_name.json',
        'unfit_geoareas.json',
        'unfit_tags.json',
        'unfit_subv_disable_all_tag.json',
        'unfit_week_day.json',
        'unfit_order_start.json',
        'unfit_workshift.json',
        'unfit_activity_points.json',
        'unfit_cancelled_by_cash.json',
        'unfit_closed_without_accept.json',
        'unfit_completed_by_dispatcher.json',
        'unfit_tariff_classes.json',
        'due_later_than_completed_at.json',
        'no_driver_accept_time.json',
        'do_not_measure_on_order_time.json',
        'order_with_cost_for_driver.json',
        'unfit_profile_payment_type_restrictions.json',
        'unfit_tags_with_inverted_relaxation.json',
        'unfit_activity_points_with_inverted_relaxation.json',
        'unfit_profile_payment_type_restrictions_with_inverted_relaxation'
        '.json',
        'unfit_tags_with_inverted_relaxation.json',
        'unfit_tariff_classes_with_inverted_relaxation.json',
        'corp_without_vat.json',
    ],
)
def test_on_order_ready_for_billing(test_data_json, load_py_json_dir):
    test_data = load_py_json_dir(
        'test_on_order_ready_for_billing', test_data_json,
    )
    event = test_data['event']
    rule = test_data['rule']
    balances = test_data['balances']
    expected_event_handled = test_data['expected_event_handled']
    actual_event_handled = rule.on_order_ready_for_billing(
        event,
        models.PaymentLevel.zero(event.order.currency),
        balances,
        driver_mode=models.DriverModeContext(None),
        log_extra=None,
    )
    assert expected_event_handled == actual_event_handled


@pytest.mark.parametrize(
    'rule_json, order_event_json, expected_documents_json',
    [
        (
            'rule.json',
            'order_subvention_changed.json',
            'non_empty_journal.json',
        ),
        (
            'rule.json',
            'subv_disable_all_order_subvention_changed.json',
            'non_empty_journal_for_subv_disable_all.json',
        ),
        (
            'rule.json',
            'spb_order_subvention_changed.json',
            'empty_journal.json',
        ),
        (
            'rule_with_inverted_relaxation.json',
            'order_subvention_changed.json',
            'non_empty_journal_for_inverted_relaxation.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_on_order_subvention_changed(
        rule_json, order_event_json, expected_documents_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    rule: models.GeoBookingRule
    order_event: models.OrderSubventionChangedEvent
    expected_documents: tp.List[models.Document]
    rule, order_event, expected_documents = load_py_json_dir(
        'test_on_order_subvention_changed',
        rule_json,
        order_event_json,
        expected_documents_json,
    )
    result = rule.on_order_subvention_changed(order_event, log_extra=None)
    assert expected_documents == result.journal.journal_entries
