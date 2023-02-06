import json

import pytest
from tt_main.output import create_error_message, print_json_format


def test_create_error_message_empty_list():
    assert create_error_message([], "OK") == "OK"


def test_create_error_message_indirect_empty_list():
    msg = []
    assert create_error_message([*msg], "OK") == "OK"


def test_create_error_message_one_string():
    msg = "Houston, we have a problem"
    assert create_error_message([msg], "OK") == msg


def test_create_error_message_multiple_strings():
    msg = "Houston, we have a problem"
    msg2 = "Not really..."
    msg3 = "But maybe we do!"
    assert create_error_message([msg, msg2, msg3], "OK") == msg + "; " + msg2 + "; " + msg3


def test_print_json_format_invalid_status():
    with pytest.raises(ValueError):
        print_json_format("test_service", "all is OK", "COOL")


def test_print_json_format_invalid_tag():
    with pytest.raises(ValueError):
        print_json_format("test_service", "all is OK", "OK", tags=["heat", 28, "test"])


def test_print_json_format_ok(capsys):
    service = "test_service"
    descr = "all is OK"
    status = "OK"
    tags = ["heat", "test"]
    print_json_format(service, descr, status, exit=False, tags=tags, sync_to_heat=False)
    captured = capsys.readouterr()
    result = json.loads(captured.out)["events"][0]
    assert result["service"] == service
    assert result["description"] == descr
    assert result["status"] == status
    assert sorted(result["tags"]) == tags
