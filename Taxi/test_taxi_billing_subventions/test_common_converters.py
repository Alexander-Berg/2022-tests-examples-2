import dataclasses
import typing as tp

import attr
import pytest

from taxi_billing_subventions.common import converters
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common import views


@pytest.mark.parametrize(
    'input_json, expected_rules_json',
    [
        ('whole_week_input.json', 'expected_whole_week_rules.json'),
        ('monday_friday_input.json', 'expected_monday_friday_rules.json'),
    ],
)
@pytest.mark.nofilldb()
def test_convert_to_daily_guarantee_rule(
        input_json, expected_rules_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    input_: views.DailyGuaranteeInput
    expected_rules: tp.List[models.DailyGuaranteeRule]
    input_, expected_rules = load_py_json_dir(
        'test_convert_to_daily_guarantee_rule',
        input_json,
        expected_rules_json,
    )
    actual_rules = converters.convert_to_daily_guarantee_rules(input_)
    assert actual_rules == expected_rules


@pytest.mark.parametrize(
    'data_json, expected_doc_json',
    [
        ('data.json', 'expected_doc.json'),
        (
            'with_toll_road_payment_price.json',
            'with_toll_road_payment_price_expected_doc.json',
        ),
        (
            'without_hiring_value_data.json',
            'without_hiring_value_expected_doc.json',
        ),
        ('with_created_data.json', 'with_created_expected_doc.json'),
    ],
)
@pytest.mark.nofilldb()
def test_convert_to_order_ready_for_billing(
        data_json, expected_doc_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    data, expected_doc = load_py_json_dir(
        'test_convert_to_order_ready_for_billing',
        data_json,
        expected_doc_json,
    )
    actual_doc = converters.convert_to_order_ready_for_billing_doc(data)
    assert dataclasses.asdict(actual_doc) == dataclasses.asdict(expected_doc)


@pytest.mark.parametrize(
    'data_json, expected_doc_json', [('data.json', 'expected_doc.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_order_subvention_changed_event(
        data_json, expected_doc_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    data, expected_doc = load_py_json_dir(
        'test_convert_to_order_subvention_changed_event',
        data_json,
        expected_doc_json,
    )
    actual_doc = converters.convert_to_order_subvention_changed_event(data)
    assert actual_doc == expected_doc


@pytest.mark.parametrize(
    'data_json, expected_doc_json', [('data.json', 'expected_doc.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_order_commission_changed_event(
        data_json, expected_doc_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    data, expected_doc = load_py_json_dir(
        'test_convert_to_order_commission_changed_event',
        data_json,
        expected_doc_json,
    )
    actual_doc = converters.convert_to_order_commission_changed_event(data)
    assert actual_doc == expected_doc


@pytest.mark.parametrize(
    'doc_json',
    [
        'doc.json',
        'doc_with_none_modified_minimal_cost.json',
        'doc_with_none_optionals.json',
    ],
)
@pytest.mark.nofilldb()
def test_order_ready_for_billing_conversion_round_trip(
        doc_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    doc = load_py_json_dir(
        'test_order_ready_for_billing_conversion_round_trip', doc_json,
    )
    data = models.doc.convert_order_ready_for_billing_to_json(doc)
    doc_after_round_trip = converters.convert_to_order_ready_for_billing_doc(
        data,
    )
    assert doc_after_round_trip == doc


@pytest.mark.parametrize(
    'data_json, expected_antifraud_query_json',
    [
        ('order_data.json', 'order_antifraud_query.json'),
        ('driver_data.json', 'driver_antifraud_query.json'),
        ('noop_data.json', 'noop_antifraud_query.json'),
        (
            'driver_with_driver_fix_data.json',
            'driver_with_driver_fix_antifraud_query.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_convert_to_antifraud_query(
        data_json, expected_antifraud_query_json, load_py_json_dir,
):
    data, expected_antifraud_query = load_py_json_dir(
        'test_convert_to_antifraud_query',
        data_json,
        expected_antifraud_query_json,
    )
    actual_antifraud_query = converters.convert_to_antifraud_query(data)
    assert attr.asdict(expected_antifraud_query) == attr.asdict(
        actual_antifraud_query,
    )
