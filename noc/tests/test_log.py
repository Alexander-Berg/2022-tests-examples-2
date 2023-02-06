import json

from tt_main.log import read_log_offset, save_log_offset


def test_read_log_offset_logname_no_logname(tmp_path):
    content = {"/var/log/keepalived.log": "9100"}
    p = tmp_path / "offsets.log"
    p.write_text(json.dumps(content))
    status, result = read_log_offset(p)
    assert status is True
    assert len(result) == 1
    assert "/var/log/keepalived.log" in result
    assert result["/var/log/keepalived.log"] == "9100"


def test_read_log_offset_logname_not_found(tmp_path):
    content = {"/var/log/keepalived.log": "9100"}
    p = tmp_path / "offsets.log"
    p.write_text(json.dumps(content))
    status, _ = read_log_offset(p, logname="/var/log/some.log")
    assert status is False


def test_read_log_offset_logname_logname_found(tmp_path):
    content = {"/var/log/bootstrap.log": "1600", "/var/log/btmp": "716"}
    p = tmp_path / "offsets.log"
    p.write_text(json.dumps(content))
    status, result = read_log_offset(p, logname="/var/log/btmp")
    assert status is True
    assert result == "716"


def test_read_log_offset_file_not_found(tmp_path):
    status, result = read_log_offset("/tmp/not_exist")
    assert status is False
    assert "No such file" in result


def test_save_log_offset_create_new_file(tmp_path):
    p = tmp_path / "offsets.log"
    assert not p.exists()
    status, result = save_log_offset(p, "/var/log/keepalived.log", offset=500)
    assert status is True
    assert result == "dumped"
    assert p.exists()
    data = json.loads(p.read_text())
    assert len(data) == 1
    assert "/var/log/keepalived.log" in data
    assert data["/var/log/keepalived.log"] == 500


def test_save_log_offset_write(tmp_path):
    content = {"/var/log/keepalived.log": "9100"}
    p = tmp_path / "offsets.log"
    p.write_text(json.dumps(content))
    assert p.exists()
    status, result = save_log_offset(p, "/var/log/keepalived.log", offset=10200)
    assert status is True
    assert result == "dumped"
    status, _ = save_log_offset(p, "/var/log/btmp", offset=500)
    assert status is True
    data = json.loads(p.read_text())
    assert len(data) == 2
    assert "/var/log/keepalived.log" in data
    assert data["/var/log/keepalived.log"] == 10200
    assert "/var/log/btmp" in data
    assert data["/var/log/btmp"] == 500
