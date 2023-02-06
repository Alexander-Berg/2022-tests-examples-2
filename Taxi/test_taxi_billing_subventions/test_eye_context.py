import pytest

from taxi_billing_subventions import eye


@pytest.mark.parametrize(
    'test_case_json', ['unique_tags.json', 'duplicate_tags.json'],
)
@pytest.mark.nofilldb()
def test_all_tags(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    context = test_case['context']
    assert context.all_tags == test_case['expected']


@pytest.mark.parametrize('test_case_json', ['empty.json'])
@pytest.mark.nofilldb
def test_empty(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    assert eye.Context.empty() == test_case['expected']


@pytest.mark.parametrize('test_case_json', ['with_extra_tags.json'])
@pytest.mark.nofilldb()
def test_with_extra_tags(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    context = test_case['context']
    tags = test_case['tags']
    assert context.with_extra_tags(tags) == test_case['expected']
