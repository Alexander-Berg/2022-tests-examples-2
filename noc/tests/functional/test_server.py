import ipaddress
import subprocess
import time
from pathlib import Path

import requests

CMD_TIMEOUT = 2
NFTABLES_CONF = "/etc/nftables.conf"
TEST_IPS = frozenset(["172.16.0.10", "172.16.0.20", "172.16.0.30", "[fd00::10]", "[fd00::20]", "[fd00::30]"])
STOP_FILE = "/run/dnsl3r_stop"


def run_cmd(command):
    result = subprocess.run(command.split(" "), capture_output=True, timeout=CMD_TIMEOUT, check=True, text=True)
    return result.stdout


def install_rule(ip):
    ip_address = ipaddress.ip_address(ip)
    ip_line = f"ip6 daddr {ip}/128" if ip_address.version == 6 else f"ip daddr {ip}/32"
    with open(NFTABLES_CONF, "r+", encoding="utf-8") as nftables_config_file:
        lines = nftables_config_file.readlines()
        nftables_config_file.seek(0)
        nftables_config_file.truncate()
        for line in lines:
            if '"lo"' in line:
                nftables_config_file.writelines([f"{ip_line} udp dport 53 drop\n", f"{ip_line} tcp dport 53 drop\n"])
            nftables_config_file.write(line)
    run_cmd("systemctl restart nftables.service")


def remove_rule(ip):
    with open(NFTABLES_CONF, "r+", encoding="utf-8") as nftables_config_file:
        lines = nftables_config_file.readlines()
        nftables_config_file.seek(0)
        nftables_config_file.truncate()
        for line in lines:
            if ip in line:
                continue
            nftables_config_file.write(line)
    run_cmd("systemctl restart nftables.service")


def check_all_ips():
    results = {}
    for ip in TEST_IPS:
        response = requests.get(f"http://{ip}/slb_check")
        results[ip.strip("[]")] = (response.status_code, response.text)
    return results


def test_all_is_up():
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200


def test_break_one():
    install_rule("172.16.0.20")
    time.sleep(1)
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200
    time.sleep(4)
    results = check_all_ips()
    for ip, response in results.items():
        status_code, _ = response
        if ip == "172.16.0.20":
            assert status_code == 503
        else:
            assert status_code == 200
    remove_rule("172.16.0.20")
    time.sleep(4)
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200


def test_break_two():
    install_rule("172.16.0.20")
    install_rule("fd00::30")
    time.sleep(1)
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200
    time.sleep(4)
    results = check_all_ips()
    for ip, response in results.items():
        status_code, _ = response
        if ip in ("172.16.0.20", "fd00::30"):
            assert status_code == 503
        else:
            assert status_code == 200
    remove_rule("172.16.0.20")
    time.sleep(4)
    results = check_all_ips()
    for ip, response in results.items():
        status_code, _ = response
        if ip == "fd00::30":
            assert status_code == 503
        else:
            assert status_code == 200
    remove_rule("fd00::30")
    time.sleep(4)
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200


def test_no_such_ip():
    response = requests.get("http://[::1]/slb_check")
    assert response.status_code == 404


def test_ready_handler():
    response = requests.get("http://[::1]/ready")
    assert response.status_code == 200


def test_stop_file():
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200
    stop_file_path = Path(STOP_FILE)
    stop_file_path.touch()
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 503
    stop_file_path.unlink()
    results = check_all_ips()
    for response in results.values():
        status_code, _ = response
        assert status_code == 200
