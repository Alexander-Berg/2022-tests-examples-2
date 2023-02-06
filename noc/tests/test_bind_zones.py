import time
from unittest.mock import patch

import pytest
from bind_zones import (check_zone_file, check_zone_freshness,
                        get_zones_from_config)


def test_get_zones(tmp_path):
    content = """
    zone "some.test" {
    type slave;
    file "/etc/bind/slave/some.test";
};
zone "other.test" {
    type slave;
    file "/etc/bind/slave/other.test";
};"""
    p = tmp_path / "bind.conf"
    p.write_text(content)
    zones = get_zones_from_config(p)
    assert len(zones) == 2
    assert "/etc/bind/slave/some.test" in zones


def test_no_bind_config():
    with pytest.raises(OSError):
        get_zones_from_config("/tmp/non_existent_path")


def test_empty_config(tmp_path):
    content = " "
    p = tmp_path / "bind.conf"
    p.write_text(content)
    assert len(get_zones_from_config(p)) == 0


def test_no_zone_file():
    test_file = "/tmp/non_existent_path"
    result = check_zone_file(test_file)
    assert len(result) == 3
    assert result["file_status"] == "file not found"
    assert result["file"] == test_file
    assert result["mtime"] is None


def test_small_zone_file(tmp_path):
    content = " "
    p = tmp_path / "some.test"
    p.write_text(content)
    result = check_zone_file(p)
    assert len(result) == 3
    assert "file size is less than" in result["file_status"]
    assert result["file"] == p
    assert result["mtime"] is None


def test_zone_file_is_ok(tmp_path):
    p = tmp_path / "other.test"
    p.write_bytes(bytes(2048))
    result = check_zone_file(p)
    assert len(result) == 3
    assert result["file_status"] == "OK"
    assert result["file"] == p
    assert time.time() - result["mtime"] < 1


def test_zone_freshness_fresh_file(tmp_path):
    status, _ = check_zone_freshness("some.test", time.time())
    assert status is True


def test_zone_freshness_no_local_result():
    with patch("bind_zones.make_cmd_call", return_value=["ERROR ERROR"]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert "local query abnormal result" in message


def test_zone_freshness_local_resolve_abnormal_sn():
    with patch("bind_zones.make_cmd_call",
               return_value=["ns.some.test. admin.some.test. XXX"]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert "local query abnormal result" in message


def test_zone_freshness_no_authoritatives():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 816"], []]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert "query for authoritative servers failed" in message


def test_zone_freshness_no_authoritative_server_reply():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 816"],
                            ["ns.some.test.", "nsb.some.test."],
                            [";;; connection timeout"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert "query to ns.some.test. returned abnormal" in message


def test_zone_freshness_nok():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 2010111015"],
                            ["ns.some.test.", "nsb.some.test."],
                            ["ns.some.test. admin.some.test. 2010111115"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert message == "some.test is outdated"


def test_zone_freshness_ok():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 2010111110"],
                            ["ns.some.test.", "nsb.some.test."],
                            ["ns.some.test. admin.some.test. 2010111115"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is True
    assert message is None


def test_negative_diff_ok():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 2010111182"],
                            ["ns.some.test.", "nsb.some.test."],
                            ["ns.some.test. admin.some.test. 2010111104"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is True
    assert message is None


def test_negative_diff_nok():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 2010111182"],
                            ["ns.some.test.", "nsb.some.test."],
                            ["ns.some.test. admin.some.test. 2010111156"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert message == "some.test is outdated"


def test_abnormal_negative_diff():
    with patch("bind_zones.make_cmd_call",
               side_effect=[["ns.some.test. admin.some.test. 2010111282"],
                            ["ns.some.test.", "nsb.some.test."],
                            ["ns.some.test. admin.some.test. 2010111156"]]):
        status, message = check_zone_freshness("some.test", time.time() - 1000)
    assert status is False
    assert message == "some.test diff is abnormal (-126)"
