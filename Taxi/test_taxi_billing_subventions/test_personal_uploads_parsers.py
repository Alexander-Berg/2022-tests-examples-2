import pytest

from taxi_billing_subventions.personal_uploads import parsers


@pytest.mark.parametrize(
    'row_json, expected_json',
    [
        ('personal_goal_data.json', 'parsed_personal_goal.json'),
        ('personal_guarantee_data.json', 'parsed_personal_guarantee.json'),
        (
            'personal_goal_data_minimal_fields.json',
            'parsed_personal_goal_minimal_fields.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_parse_analytics_data(row_json, expected_json, load_py_json_dir):
    input_row, expected_row = load_py_json_dir(
        'test_parse_analytics_data', row_json, expected_json,
    )
    parsed = parsers.parse_analytics_data(input_row)
    assert parsed == expected_row


@pytest.mark.parametrize(
    'input_json',
    [
        'bad_analytics_data.json',
        'bad_unique_driver_id.json',
        'bad_driver_id.json',
        'no_begin_time.json',
        'null_begin_time.json',
        'invalid_begin_time.json',
        'no_orders_kpi.json',
        'null_orders_kpi.json',
        'invalid_orders_kpi.json',
        'no_bonus_sum.json',
        'null_bonus_sum.json',
        'invalid_bonus_sum.json',
        'invalid_phones.json',
        'invalid_geoareas.json',
        'invalid_time_intervals.json',
    ],
)
@pytest.mark.nofilldb()
# pylint: disable=invalid-name
def test_parse_analytics_data_failure(input_json, load_py_json_dir):
    input_row = load_py_json_dir(
        'test_parse_analytics_data_failure', input_json,
    )
    with pytest.raises(parsers.ParseError):
        parsers.parse_analytics_data(input_row)
