import pytest
import pytz

from taxi_billing_subventions import common
from taxi_billing_subventions.personal_uploads import converters


@pytest.mark.parametrize(
    'row_json, expected_rule_json',
    [
        ('guarantee_row.json', 'guarantee_rule.json'),
        ('goal_row.json', 'goal_rule.json'),
    ],
)
@pytest.mark.now('2018-05-09T00:00:00+0300')
@pytest.mark.nofilldb()
# pylint: disable=invalid-name
def test_convert_analytics_row_to_rule(
        row_json, expected_rule_json, load_py_json_dir,
):
    rule_row, expected_rule = load_py_json_dir(
        'test_convert_analytics_row_to_rule', row_json, expected_rule_json,
    )
    actual_rule = converters.convert_analytics_row_to_rule(
        rule_row, _moscow_zone(),
    )

    assert actual_rule == expected_rule


@pytest.mark.parametrize(
    'row_json, expected_exception',
    [
        ('too_long_goal.json', converters.ConvertError),
        ('started_in_the_past_guarantee.json', converters.ConvertError),
    ],
)
@pytest.mark.now('2018-05-10T00:00:00+0300')
@pytest.mark.nofilldb()
# pylint: disable=invalid-name
def test_convert_analytics_row_to_rule_failure(
        row_json, expected_exception, load_py_json_dir,
):
    rule_row = load_py_json_dir(
        'test_convert_analytics_row_to_rule_failure', row_json,
    )
    with pytest.raises(expected_exception):
        rule = converters.convert_analytics_row_to_rule(
            rule_row, _moscow_zone(),
        )
        rule.validate()


def _moscow_zone():
    return common.models.Zone(
        name='moscow',
        city_id='Москва',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=common.models.Vat.make_naive(12000),
        country='rus',
    )
