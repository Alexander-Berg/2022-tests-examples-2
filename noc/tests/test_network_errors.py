import copy
import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from network_errors import check_network_errors, parse_interfaces_stat, write_timestamp
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

prev_run_timestamp_file = "/tmp/monitoring_network_errors_timestamp.prev"


@pytest.fixture
def clean_timestamp():
    import os

    cleaned = False

    try:
        os.remove(prev_run_timestamp_file)
        cleaned = True
    except FileNotFoundError:
        pass

    return cleaned


def create_fake_stats(ts_diff=300):
    """Creates fake interface statistics, softnet data and timestamp to
    emulate parsed data from prev files.
    Attributes:
        ts_diff (default - 300) - seconds to extract from current time to get
            timestamp in the past
    Returns:
        dict with interfaces statistics (eth0 and eth1), list with softnet
        dicts (two CPU cores) and timestamp that was ts_diff seconds ago
    TODO: provide args to gen variable numbers of interfaces and CPUs.
    """
    int_stat_dict = {
        "eth0": {
            "rx_over_errors": 0,
            "tx_window_errors": 0,
            "tx_aborted_errors": 0,
            "rx_compressed": 0,
            "rx_nohandler": 0,
            "tx_carrier_errors": 0,
            "collisions": 0,
            "tx_packets": 1000,
            "tx_dropped": 0,
            "rx_packets": 1000,
            "rx_length_errors": 0,
            "rx_missed_errors": 0,
            "tx_bytes": 10002,
            "rx_frame_errors": 0,
            "rx_dropped": 0,
            "rx_crc_errors": 0,
            "rx_bytes": 13241,
            "tx_errors": 0,
            "rx_fifo_errors": 0,
            "tx_fifo_errors": 0,
            "tx_heartbeat_errors": 0,
            "multicast": 0,
            "rx_errors": 0,
            "tx_compressed": 0,
            "rx_no_dma_resources": 0,
        },
        "eth1": {
            "rx_over_errors": 0,
            "tx_window_errors": 0,
            "tx_aborted_errors": 0,
            "rx_compressed": 0,
            "rx_nohandler": 0,
            "tx_carrier_errors": 0,
            "collisions": 0,
            "tx_packets": 312,
            "tx_dropped": 0,
            "rx_packets": 814,
            "rx_length_errors": 0,
            "rx_missed_errors": 0,
            "tx_bytes": 1562,
            "rx_frame_errors": 0,
            "rx_dropped": 0,
            "rx_crc_errors": 0,
            "rx_bytes": 8316,
            "tx_errors": 0,
            "rx_fifo_errors": 0,
            "tx_fifo_errors": 0,
            "tx_heartbeat_errors": 0,
            "multicast": 0,
            "rx_errors": 0,
            "tx_compressed": 0,
            "rx_no_dma_resources": 0,
        },
    }
    softnet_data = [
        {
            "received_rps": 0,
            "time_squeeze": 0,
            "cpu_collision": 0,
            "processed": 50,
            "flow_limit_count": 0,
            "dropped": 0,
        },
        {
            "received_rps": 0,
            "time_squeeze": 0,
            "cpu_collision": 0,
            "processed": 1309,
            "flow_limit_count": 0,
            "dropped": 0,
        },
    ]
    timestamp = time.time() - ts_diff
    return int_stat_dict, softnet_data, timestamp


def write_files(int_stat_dict, softnet_data, timestamp):
    """Dumps JSON formatted data in prev files to be read by
    check_network_errors.
    Arguments:
     * int_stat_dict - dict with interfaces statistics
     * softnet_data - list with softnet data dicts
     * timestamp
    Returns nothing.
    """
    with open("/tmp/monitoring_network_errors_softnet.prev", "w") as wr_fd:
        json.dump(softnet_data, wr_fd)
    with open("/tmp/monitoring_network_errors_statistics.prev", "w") as wr_fd:
        json.dump(int_stat_dict, wr_fd)
    with open("/tmp/monitoring_network_errors_timestamp.prev", "w") as wr_fd:
        json.dump({"time": timestamp}, wr_fd)


def test_no_errors():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_packets"] = 10000000
    int_stat_dict["eth0"]["tx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert msg == "OK"
    assert status == OK_STATUS


def test_eth1_tx_dropped_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth1"]["tx_dropped"] = 1600
    int_stat_dict["eth1"]["tx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth1 tx_dropped = 0.0" in msg
    assert status == CRIT_STATUS


def test_eth1_tx_dropped_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth1"]["tx_dropped"] = 600
    int_stat_dict["eth1"]["tx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth1 tx_dropped = 0.00" in msg
    assert status == WARN_STATUS


def test_eth0_rx_dropped_too_little_to_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_dropped"] = 5
    int_stat_dict["eth0"]["rx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "OK" in msg
    assert status == OK_STATUS


def test_multiple_interfaces_errors_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_dropped"] = 100
    int_stat_dict["eth0"]["rx_packets"] = 10000000
    int_stat_dict["eth1"]["tx_carrier_errors"] = 2232
    int_stat_dict["eth1"]["tx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth1 tx_carrier_errors = " in msg
    assert "eth0 rx_dropped = " in msg
    assert status == CRIT_STATUS


def test_softnet_cpu1_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data[1]["received_rps"] = 10000000
    softnet_data[1]["dropped"] = 1672
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "CPU 1 dropped = 0.0" in msg
    assert status == CRIT_STATUS


def test_softnet_cpu1_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data[1]["received_rps"] = 10000000
    softnet_data[1]["dropped"] = 812
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "CPU 1 dropped = 0.0" in msg
    assert status == WARN_STATUS


def test_softnet_cpu1_too_little_to_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data[1]["dropped"] = 9
    softnet_data[1]["received_rps"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "OK" in msg
    assert status == OK_STATUS


def test_softnet_multiple_cpu_drops_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data[0]["received_rps"] = 10000000
    softnet_data[0]["dropped"] = 2422
    softnet_data[1]["received_rps"] = 10000000
    softnet_data[1]["dropped"] = 812
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "CPU 0 dropped =" in msg and "CPU 1 dropped =" in msg
    assert status == CRIT_STATUS


def test_multiple_interfaces_errors_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["tx_carrier_errors"] = 14
    int_stat_dict["eth0"]["tx_packets"] = 10000000
    int_stat_dict["eth1"]["rx_packets"] = 10000000
    int_stat_dict["eth1"]["rx_crc_errors"] = 18
    int_stat_dict["eth1"]["rx_length_errors"] = 15
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth0 tx_carrier" in msg and "eth1 rx_crc" in msg and "eth1 rx_length" in msg
    assert status == WARN_STATUS


def test_both_softnet_and_interfaces_errors_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data[0]["dropped"] = 2422
    softnet_data[0]["received_rps"] = 10000000
    int_stat_dict["eth1"]["tx_carrier_errors"] = 2232
    int_stat_dict["eth1"]["tx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "CPU 0 dropped = " in msg and "eth1 tx_carrier_errors = " in msg
    assert status == CRIT_STATUS


def test_no_dropped_field_in_softnet():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    del softnet_data[0]["dropped"]
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "dropped field not exists" in msg
    assert status == CRIT_STATUS


def test_no_tx_window_errors_field_eth1():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    del int_stat_dict["eth1"]["tx_window_errors"]
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth1"]["tx_window_errors"] = 15
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth1/tx_window_errors not exists" in msg
    assert status == CRIT_STATUS


def test_no_eth0_statistics():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    save_eth0 = copy.copy(int_stat_dict["eth0"])
    del int_stat_dict["eth0"]
    int_stat_dict["eth2"] = save_eth0
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"] = save_eth0
    del int_stat_dict["eth2"]
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth0 not exists" in msg
    assert status == CRIT_STATUS


def test_incorrect_timestamp():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, "zbz")
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", "zbz"),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "incorrect timestamp" in msg
    assert status == CRIT_STATUS


def test_timestamp_ahead():
    int_stat_dict, softnet_data, _ = create_fake_stats()
    write_files(int_stat_dict, softnet_data, time.time() + 1500)
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", time.time() + 1500),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "timestamp ahead" in msg
    assert status == CRIT_STATUS


def test_stale_timestamp():
    int_stat_dict, softnet_data, _ = create_fake_stats()
    write_files(int_stat_dict, softnet_data, time.time() - 8000)
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", time.time() - 8000),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "was long ago" in msg
    assert status == CRIT_STATUS


def test_diff_len_stats():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth3"] = copy.copy(int_stat_dict["eth0"])
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "different len between statistic" in msg
    assert status == CRIT_STATUS


def test_different_len_softnet():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    softnet_data.append(copy.copy(softnet_data[0]))
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "different len between state" in msg
    assert status == CRIT_STATUS


def test_rx_no_dma_resources_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth1"]["rx_no_dma_resources"] = 1700
    int_stat_dict["eth1"]["rx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth1 rx_no_dma_resources =" in msg
    assert status == CRIT_STATUS


def test_parse_interfaces_stat_ok(tmpdir):
    counter = "10"
    file_list = [
        "rx_over_errors",
        "tx_window_errors",
        "tx_aborted_errors",
        "rx_compressed",
        "rx_nohandler",
        "tx_carrier_errors",
        "collisions",
        "tx_packets",
        "tx_dropped",
        "rx_packets",
        "rx_length_errors",
        "rx_missed_errors",
        "tx_bytes",
        "rx_frame_errors",
        "rx_dropped",
        "rx_crc_errors",
        "rx_bytes",
        "tx_errors",
        "rx_fifo_errors",
        "tx_fifo_errors",
        "tx_heartbeat_errors",
        "multicast",
        "rx_errors",
        "tx_compressed",
    ]
    for interface in ["eth0", "eth1"]:
        int_path = tmpdir.mkdir(interface).mkdir("statistics")
        for filename in file_list:
            _file = int_path.join(filename)
            _file.write(counter)
    with patch("network_errors.make_cmd_call", return_value=["  rx_no_dma_resources: 0"]):
        _, int_stats = parse_interfaces_stat(sys_class=str(tmpdir))
    assert int_stats["eth1"]["rx_fifo_errors"] == 10
    assert len(int_stats["eth0"]) == 25


def test_parse_interfaces_stat_no_rx_dma_resources_collecting_and_ok(tmpdir):
    counter = "10"
    file_list = [
        "rx_over_errors",
        "tx_window_errors",
        "tx_aborted_errors",
        "rx_compressed",
        "rx_nohandler",
        "tx_carrier_errors",
        "collisions",
        "tx_packets",
        "tx_dropped",
        "rx_packets",
        "rx_length_errors",
        "rx_missed_errors",
        "tx_bytes",
        "rx_frame_errors",
        "rx_dropped",
        "rx_crc_errors",
        "rx_bytes",
        "tx_errors",
        "rx_fifo_errors",
        "tx_fifo_errors",
        "tx_heartbeat_errors",
        "multicast",
        "rx_errors",
        "tx_compressed",
    ]
    for interface in ["eth0", "eth1"]:
        int_path = tmpdir.mkdir(interface).mkdir("statistics")
        for filename in file_list:
            _file = int_path.join(filename)
            _file.write(counter)
    with patch("network_errors.make_cmd_call", side_effect=[[""], ["rx_no_dma_resources: 1500"]]):
        _, int_stats = parse_interfaces_stat(sys_class=str(tmpdir))
    assert int_stats["eth1"]["rx_no_dma_resources"] == 0
    assert int_stats["eth0"]["rx_no_dma_resources"] == 1500
    assert len(int_stats["eth0"]) == 25


def test_counter_updates_if_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_over_errors"] = 512
    int_stat_dict["eth0"]["rx_packets"] = 10000000
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    with open("/tmp/monitoring_network_errors_statistics.prev", "r") as rfd:
        after_stats = json.load(rfd)
    assert after_stats["eth0"]["rx_over_errors"] == 512
    assert "eth0 rx_over_errors" in msg
    assert status == WARN_STATUS


def test_counter_updates_if_no_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_over_errors"] = 222
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    with open("/tmp/monitoring_network_errors_statistics.prev", "r") as rfd:
        after_stats = json.load(rfd)
    assert after_stats["eth0"]["rx_over_errors"] == 222
    assert msg == "OK"
    assert status == OK_STATUS


def test_eth0_rx_dropped_warn():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_packets"] = 10001000
    int_stat_dict["eth0"]["rx_dropped"] = 11
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth0 rx_dropped = 0.0001 %" in msg
    assert status == WARN_STATUS


def test_eth0_rx_dropped_crit():
    int_stat_dict, softnet_data, timestamp = create_fake_stats()
    write_files(int_stat_dict, softnet_data, timestamp)
    int_stat_dict["eth0"]["rx_packets"] = 10001000
    int_stat_dict["eth0"]["rx_dropped"] = 1010
    mock_methods = [
        ("parse_interfaces_stat", int_stat_dict),
        ("parse_softnet_stat", softnet_data),
        ("write_timestamp", timestamp),
    ]
    for mocked_method in mock_methods:
        patcher = patch("network_errors." + mocked_method[0], return_value=(True, mocked_method[1]))
        patcher.start()
    status, msg, _ = check_network_errors()
    assert "eth0 rx_dropped = 0.01" in msg
    assert status == CRIT_STATUS


def test_write_timestamp_ok(clean_timestamp):
    ct = time.time()
    ts = {"time": ct}
    p = Path(prev_run_timestamp_file)
    p.write_text(json.dumps(ts))
    status, result = write_timestamp(ct + 1010)
    assert status
    assert int(json.loads(p.read_text())["time"]) - ct > 1000
    assert result == ct


def test_write_timestamp_creation(clean_timestamp):
    ct = time.time()
    status, result = write_timestamp(ct, create=True)
    assert status
    assert not result


def test_write_timestamp_no_file(clean_timestamp):
    ct = time.time()
    status, result = write_timestamp(ct)
    assert not status
    assert "Expecting value" in str(result)
