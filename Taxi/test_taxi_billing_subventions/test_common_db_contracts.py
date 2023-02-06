import pytest

from taxi_billing_subventions.common import db


@pytest.mark.parametrize('test_case_json', ['convert_json.json'])
@pytest.mark.nofilldb()
def test_convert_json_to_contract(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    json = test_case['json']
    contract = test_case['contract']
    assert db.convert_to_contract(json) == contract
