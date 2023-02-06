import pytest
import json

from contribs.forms import parse_answer

def json_load(fpath):
    with open(fpath, "rb") as f:
        return json.load(f)


@pytest.mark.parametrize("answer_data_json,form_info_json,expected_json",
                         [("answer_data_3.json", "form_info_3.json", "expected_3.json")])
def test_parse_answer(datadir, answer_data_json, form_info_json, expected_json):
    answer_data = json_load(datadir / answer_data_json)
    fields_info = json_load(datadir / form_info_json)["fields"]
    expected = json_load(datadir / expected_json)
    assert expected["attributes"] == parse_answer(answer_data, fields_info)["attributes"]
