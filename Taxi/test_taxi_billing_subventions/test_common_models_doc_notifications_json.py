import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'test_case_json',
    [
        'goal_notification_with_str.json',
        'goal_notification_with_object_id.json',
    ],
)
def test_convert_goal_notification(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    input_ = test_case['input']
    actual = models.doc.convert_goal_notification_to_json(input_)
    assert test_case['expected'] == actual
    assert input_ == models.doc.convert_json_to_notification(actual)


@pytest.mark.parametrize(
    'test_case_json', ['daily_guarantee_notification.json'],
)
def test_convert_daily_guarantee_notification_json(
        test_case_json, load_py_json,
):
    # pylint: disable=invalid-name
    test_case = load_py_json(test_case_json)
    input_ = test_case['input']
    actual = models.doc.convert_daily_guarantee_notification_to_json(input_)
    assert test_case['expected'] == actual
    assert input_ == models.doc.convert_json_to_notification(actual)
