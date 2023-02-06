import pytest
import demjson

from sandbox.projects.yabs.qa.response_tools.parse_json import try_parse_json, try_parse_json_with_timeout


@pytest.mark.parametrize(("json_str", "expected_object", "expected_errors"), [
    ('{"test":1}', {"test": 1}, []),
    ('{"test":1}', {"test": 1}, []),
])
def test_try_parse_json_default(json_str, expected_object, expected_errors):
    parsed, errors = try_parse_json(json_str)
    assert parsed == expected_object
    assert errors == expected_errors


@pytest.mark.parametrize(("json_str", "expected_object", "expected_errors"), [
    ('{test:1}', {"test": 1}, []),
])
def test_try_parse_json_demjson(json_str, expected_object, expected_errors):
    parsed, errors = try_parse_json(json_str, jsonp_parser=demjson.decode, allow_identifier_keys=True)
    assert parsed == expected_object
    assert errors == expected_errors


@pytest.mark.parametrize(("json_str", "expected_error_messages"), [
    ('{test:1}', ["JSON does not allow identifiers to be used as strings"]),
])
def test_try_parse_json_demjson_return_errors(json_str, expected_error_messages):
    _, errors = try_parse_json(json_str, jsonp_parser=demjson.decode, return_errors=True)
    assert [e.message for e in errors] == expected_error_messages


@pytest.mark.parametrize(("json_str", "expected_error_message"), [
    ('{test:1}', "JSON does not allow identifiers to be used as strings"),
])
def test_try_parse_json_demjson_raise_errors(json_str, expected_error_message):
    error = Exception("dummy")
    parsed = None
    try:
        parsed = try_parse_json(json_str, jsonp_parser=demjson.decode, return_errors=False)
    except Exception as exc:
        error = exc
    assert parsed is None
    assert error.message == expected_error_message


@pytest.mark.parametrize(("json_str", "expected_error_message"), [
    ('{test:2e12345678000000000000000000}', "Parsing timed out"),
])
def test_try_parse_json_demjson_timeout(json_str, expected_error_message):
    error = Exception("dummy")
    parsed = None
    try:
        parsed = try_parse_json_with_timeout(json_str, timeout=1,
                                             jsonp_parser=demjson.decode, return_errors=False, allow_identifier_keys=True)
    except Exception as exc:
        error = exc
    assert parsed is None
    assert error.message == expected_error_message
