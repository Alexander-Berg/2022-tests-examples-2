import pytest

from ipv4mgr.apps.server.api.v0.handlers.pools import (
    RAW_WKP_SUBNET,
    calculate_destination_net6,
)


@pytest.mark.parametrize(
    "mapping,expected_net6",
    [
        ({"default": True}, RAW_WKP_SUBNET),
        (
            {"default": False, "outer_ip4": "0.0.0.0"},
            "2a02:6bc::/96",
        ),
        (
            {"default": False, "outer_ip4": "255.255.255.255"},
            "2a02:6bc:ffff:ffff::/96",
        ),
        (
            {"default": False, "outer_ip4": "37.140.152.1"},
            "2a02:6bc:258c:9801::/96",
        ),
    ],
)
def test_calculate_destination_net6(mapping, expected_net6):
    actual_net6 = calculate_destination_net6(mapping)
    assert actual_net6 == expected_net6
