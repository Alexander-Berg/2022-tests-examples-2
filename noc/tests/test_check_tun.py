from unittest.mock import patch
from check_tun import parse_nfqueue


def test_parse_nfqueue_ok():
    nfq_data = ["    1  25424     0 2 65531     0     0  9166669  1"]
    with patch("check_tun.make_cmd_call", return_value=nfq_data):
        status, result = parse_nfqueue()
    assert status
    assert len(result) == 1
    assert "1" in result
    assert isinstance(result["1"], dict)
    assert result["1"]["peer_portid"] == "25424"
    assert result["1"]["id_sequence"] == "9166669"
    assert result["1"]["queue_dropped"] == "0"


def test_nfqueue_file_empty():
    with patch("check_tun.make_cmd_call", return_value=[]):
        status, result = parse_nfqueue()
    assert status
    assert isinstance(result, dict)
    assert len(result) == 0


def test_nfqueue_corrupted_line():
    nfq_data = ["    1  25424     0 2 ",
                "    2  34561     0 2 47052     0     0  3972509  2"]
    with patch("check_tun.make_cmd_call", return_value=nfq_data):
        status, result = parse_nfqueue()
    assert status
    assert len(result) == 1
    assert isinstance(result["2"], dict)
    assert result["2"]["peer_portid"] == "34561"
    assert result["2"]["id_sequence"] == "3972509"
