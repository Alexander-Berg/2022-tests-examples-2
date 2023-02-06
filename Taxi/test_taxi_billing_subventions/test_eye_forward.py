import pytest

from taxi_billing_subventions import eye


@pytest.mark.parametrize('test_case_json', ['null.json', 'not_null.json'])
@pytest.mark.nofilldb()
def test_from_json(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    actual = eye.Forward.from_json(test_case['json'])
    assert actual == test_case['expected']


@pytest.mark.parametrize('test_case_json', ['empty.json', 'not_empty.json'])
@pytest.mark.nofilldb()
def test_to_json(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    actual = test_case['forward'].to_json()
    assert actual == test_case['expected']
