import gzip
import io
import os.path
import time
from unittest.mock import Mock, patch

from balancer_agent.operations.balancer_configs.config_containers import RS, ServicesInfo, VSDistinguisher
from balancer_agent.operations.systems import yanet

from typing import BinaryIO


def set_popen_mock(popen_mock: Mock, stdout: BinaryIO) -> None:
    popen_mock.return_value.__enter__ = Mock(return_value=Mock())
    popen_mock.return_value.__enter__.return_value.stdout = stdout
    popen_mock.return_value.__exit__ = Mock()


@patch("subprocess.Popen", return_value=Mock())
def test_get_no_services(popen_mock: Mock):
    set_popen_mock(popen_mock, io.BytesIO(b"[]"))
    cli: yanet.YaNetCli = yanet.YaNetCli()
    services: ServicesInfo = cli.get_services()

    assert len(services) == 0


@patch("subprocess.Popen", return_value=Mock())
def test_get_some_services(popen_mock: Mock):
    cli: yanet.YaNetCli = yanet.YaNetCli()
    with open(os.path.join(os.path.dirname(__file__), "sample.json"), "rb") as f:
        set_popen_mock(popen_mock, f)
        services: ServicesInfo = cli.get_services()

    expected_reals = [
        RS(address="2a02:6b8:0:31d:15::0", weight=1),
        RS(address="2a02:6b8:c0e:8a:0:675:774b:c355", weight=1),
        RS(address="2a02:6b8:c0e:a0e:0:675:7c19:a382", weight=1),
    ]

    assert len(services) == 4
    assert services[VSDistinguisher(ip="87.250.234.233", port=60889, protocol="TCP")] == expected_reals
    assert services[VSDistinguisher(ip="87.250.234.233", port=60889, protocol="UDP")] == expected_reals
    assert services[VSDistinguisher(ip="2a02:6b8:0:300::29:b19b", port=60889, protocol="TCP")] == expected_reals
    assert services[VSDistinguisher(ip="2a02:6b8:0:300::29:b19b", port=60889, protocol="UDP")] == expected_reals


@patch("subprocess.Popen", return_value=Mock())
def test_get_alot_of_services(popen_mock: Mock):
    cli: yanet.YaNetCli = yanet.YaNetCli()
    with gzip.open(os.path.join(os.path.dirname(__file__), "huge.json.gz"), "rb") as f:
        set_popen_mock(popen_mock, f)
        start = time.monotonic()
        services: ServicesInfo = cli.get_services()
        elapsed = time.monotonic() - start

    assert len(services) == 460
    assert elapsed < 0.6
