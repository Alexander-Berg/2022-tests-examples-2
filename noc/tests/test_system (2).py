from unittest.mock import MagicMock, patch

from tt_main.system import (
    get_addr_show,
    make_cmd_call,
    parse_interrupts,
    parse_ipvsadm_stats,
    parse_yanet_stats,
    parse_meminfo,
    search_pids_by_cmdline,
)


def fake_cmd_result(text):
    for line in text.splitlines():
        yield line


def test_cmd_call_ok():
    lines = 0
    output = ""
    string = "line 1\nline 2\nline 3"
    for line in make_cmd_call("echo -n -e '{}'".format(string)):
        lines += 1
        output += line
    assert lines == 3
    assert "line 2" in output


def test_cmd_call_error():
    assert len(list(make_cmd_call("ls /tmp/dir_that_not_exists/"))) == 0


def test_get_addr_show():
    with open("tests/sample_texts/ip_address_example.txt", "r") as _file:
        test_output = _file.read()
    with patch("tt_main.system.make_cmd_call", side_effect=[fake_cmd_result(test_output)]):
        result = get_addr_show()
    assert len(result) == 265
    assert "93.158.134.207/32" in result["dummy12"]["inet"]
    assert "fe80::ece3:30ff:fe54:1cee/64" in result["dummy11"]["inet6"]
    assert result["bond0"]["link/ether"] == "90:e2:ba:4a:ca:e5"


def test_get_addr_show_with_filter():
    with open("tests/sample_texts/ip_address_example.txt", "r") as _file:
        test_output = _file.read()
    with patch("tt_main.system.make_cmd_call", side_effect=[fake_cmd_result(test_output)]):
        result = get_addr_show(filter_interface="eth")
    assert len(result) == 4
    assert result["eth3"]["state"] == "DOWN"
    assert "fe80::ae1f:6bff:fe46:2094/64" in result["eth2"]["inet6"]
    assert result["eth1"]["mtu"] == "9000"


def test_parse_interrupts():
    status, result = parse_interrupts(interrupts_file="tests/sample_texts/interrupts_example.txt")
    assert status is True
    assert result["146"]["description"] == "PCI-MSI 67635230-edge mlx5_comp26@pci:0000:81:00.1"
    assert result["146"]["CPU54"] == "294235"
    assert result["49"]["description"] == "PCI-MSI 526339-edge eth3-TxRx-2"
    assert result["49"]["CPU53"] == "526612"
    assert result["9"]["description"] == "IO-APIC 9-fasteoi acpi"
    assert result["9"]["CPU1"] == "2351236"


def test_parse_ipvsadm_stats_cli_execution_fail():
    with patch("tt_main.system.make_cmd_call", return_value=[]):
        status, result = parse_ipvsadm_stats()
    assert status is False
    assert len(result) == 0


def test_parse_ipvsadm_stats_no_vs():
    ipvsadm_output = """
IP Virtual Server version 1.2.1 (size=1048576)
Prot LocalAddress:Port               Conns   InPkts  OutPkts  InBytes OutBytes
  -> RemoteAddress:Port"""
    with patch("tt_main.system.make_cmd_call", return_value=ipvsadm_output.splitlines()):
        status, result = parse_ipvsadm_stats()
    assert status is True
    assert len(result) == 0


def test_parse_ipvsadm_stats_ok():
    with open("tests/sample_texts/ipvsadm_stats_example.txt", "r") as _file:
        test_output = _file.read()
    with patch("tt_main.system.make_cmd_call", side_effect=[fake_cmd_result(test_output)]):
        status, result = parse_ipvsadm_stats()
    assert status is True
    assert len(result["IPs"]) == 100
    assert result["IPs"]["93.158.157.135;443;TCP"]["stats"]["InPkts"] == "378"
    assert (
        result["IPs"]["[2a02:6b8:0:3400::3:58];80;TCP"]["members"]["[2a02:6b8:c02:516:0:1478:9094:2b76];80"]["Conns"]
        == "87"
    )
    assert len(result["FWMs"]) == 0


def test_parse_yanet_stats_cli_execution_fail():
    with patch("tt_main.system.make_cmd_call", return_value=[]):
        status, result = parse_yanet_stats()
    assert status is False
    assert len(result) == 0


def test_parse_yanet_stats_ok():
    ipvsadm_output = """[
        {
            "bytes": "9711791642321",
            "connections": "9049",
            "module": "balancer0",
            "packets": "1446083237",
            "proto": "tcp",
            "scheduler": "wrr",
            "virtual_ip": "2a02:6b8:0:3400::1:159",
            "virtual_port": "1111"
        },
        {
            "bytes": "0",
            "connections": "0",
            "module": "balancer0",
            "packets": "0",
            "proto": "tcp",
            "scheduler": "wrr",
            "virtual_ip": "2a02:6b8:0:3400::1:159",
            "virtual_port": "1443"
        },
        {
            "bytes": "0",
            "connections": "0",
            "module": "balancer0",
            "packets": "0",
            "proto": "tcp",
            "scheduler": "wrr",
            "virtual_ip": "2a02:6b8:0:3400::1:159",
            "virtual_port": "12000"
        }
    ]"""
    with patch("tt_main.system.make_cmd_call", return_value=ipvsadm_output.splitlines()):
        status, result = parse_yanet_stats()

    assert status is True
    assert len(result["IPs"]) == 3
    assert len(result["FWMs"]) == 0
    assert result["IPs"]["2a02:6b8:0:3400::1:159;1111;TCP"]["stats"]["InPkts"] == "1446083237"


def test_parse_meminfo():
    status, result = parse_meminfo(meminfo_file="tests/sample_texts/meminfo_example.txt")
    assert status is True
    assert result["MemTotal"] == "131905216 kB"
    assert result["MemAvailable"] == "96962924 kB"
    assert result["VmallocTotal"] == "34359738367 kB"


def test_search_pids_by_cmdline_no_name():
    assert search_pids_by_cmdline()[0] is False


def test_search_pids_by_cmdline_found():
    m1 = MagicMock(pid="1416")
    m1.cmdline.return_value = ["bash"]
    m2 = MagicMock(pid="817")
    m2.cmdline.return_value = ["keepalived", "--dont fork"]
    m3 = MagicMock(pid="661")
    m3.cmdline.return_value = ["urxvt"]
    with patch("tt_main.system.psutil.process_iter", return_value=[m1, m2, m3]):
        status, result = search_pids_by_cmdline(name="keepalived")
    assert status is True
    assert result[0] == "817"
    assert len(result) == 1


def test_search_pids_by_cmdline_not_found():
    m1 = MagicMock(pid="1416")
    m1.cmdline.return_value = ["bash"]
    m2 = MagicMock(pid="817")
    m2.cmdline.return_value = ["keepalived", "--dont fork"]
    m3 = MagicMock(pid="661")
    m3.cmdline.return_value = ["urxvt"]
    with patch("tt_main.system.psutil.process_iter", return_value=[m1, m2, m3]):
        status, result = search_pids_by_cmdline(name="check-tun")
    assert status is True
    assert len(result) == 0
