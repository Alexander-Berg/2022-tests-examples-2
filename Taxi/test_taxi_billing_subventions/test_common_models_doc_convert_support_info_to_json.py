import pytest


@pytest.mark.parametrize('test_case_json', ['support_info_to_json.json'])
@pytest.mark.nofilldb()
def test_convert_support_info_to_json(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    support_info = test_case['support_info']
    expected = test_case['expected']
    actual = support_info.to_json()
    assert actual == expected
