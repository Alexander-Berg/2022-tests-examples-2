import pytest

from taxi_billing_subventions.common.models import _rule_helpers


@pytest.mark.parametrize(
    'matcher_json, expected_key',
    [
        ('ride_count_matcher.json', 'ride_count'),
        ('ride_count_total_matcher.json', 'ride_count_total'),
        ('ride_count_sticker_matcher.json', 'ride_count_sticker'),
        ('ride_count_sticker_total_matcher.json', 'ride_count_sticker_total'),
        ('ride_count_fullbranding_matcher.json', 'ride_count_fullbranding'),
        (
            'ride_count_fullbranding_total_matcher.json',
            'ride_count_fullbranding_total',
        ),
        ('ride_count_fallback_matcher.json', 'ride_count'),
    ],
)
@pytest.mark.nofilldb()
def test_get_decline_reason_key(matcher_json, expected_key, load_py_json_dir):
    matcher = load_py_json_dir('test_get_decline_reason_key', matcher_json)
    actual_key = _rule_helpers.get_decline_reason_key(matcher)
    assert expected_key == actual_key


@pytest.mark.nofilldb()
def test_trim_unfit_tags_if_no_allowed(load_py_json):
    # pylint: disable=protected-access
    matcher = load_py_json('matcher.json')
    matcher.tags = ['tag1']
    math_info = matcher._match_tags(['tag2', 'tag3'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['<trimmed>']


@pytest.mark.nofilldb()
def test_dont_trim_one_tag_if_no_allowed(load_py_json):
    # pylint: disable=protected-access
    matcher = load_py_json('matcher.json')
    matcher.tags = ['tag1']
    math_info = matcher._match_tags(['tag2'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['tag2']


@pytest.mark.nofilldb()
def test_trim_unfit_tags_if_has_forbidden(load_py_json):
    matcher = load_py_json('matcher.json')
    math_info = matcher.not_match_tags(['tag1', 'tag2'], ['tag1'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['<trimmed>']


@pytest.mark.nofilldb()
def test_dont_trim_one_tagif_has_forbidden(load_py_json):
    matcher = load_py_json('matcher.json')
    math_info = matcher.not_match_tags(['tag1'], ['tag1'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['tag1']


@pytest.mark.nofilldb()
def test_trim_unfit_geoareas_if_no_allowed(load_py_json):
    matcher = load_py_json('matcher.json')
    matcher.geoareas = ['a1']
    math_info = matcher.match_geoareas(['a2', 'a3'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['<trimmed>']


@pytest.mark.nofilldb()
def test_dont_trim_one_geoarea_if_no_allowed(load_py_json):
    matcher = load_py_json('matcher.json')
    matcher.geoareas = ['a1']
    math_info = matcher.match_geoareas(['a2'])
    assert math_info.reason
    assert math_info.reason.properties.details['values'] == ['a2']
