import pytest


@pytest.mark.parametrize(
    'test_case_json',
    [
        'daily_guarantee_rule.json',
        'discount_rule.json',
        'geo_booking_rule.json',
        'goal_rule.json',
        'mfg_geo_rule.json',
        'mfg_rule.json',
        'on_top_rule.json',
        'on_top_geo_rule.json',
        'ridecount_mfg_rule.json',
        'personal_goal_rule.json',
    ],
)
@pytest.mark.nofilldb()
def test_unfit_tags(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    rule = test_case['rule']
    assert rule.unfit_tags == test_case['expected']
