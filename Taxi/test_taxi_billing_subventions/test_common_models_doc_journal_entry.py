import pytest


@pytest.mark.parametrize(
    'test_case_json', ['fit.json', 'unfit.json', 'dry_unfit.json'],
)
@pytest.mark.nofilldb()
def test_is_unfit(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    assert test_case['journal_entry'].is_unfit is test_case['expected']
