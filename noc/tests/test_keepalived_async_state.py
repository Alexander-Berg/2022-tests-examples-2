from unittest import TestCase
from unittest.mock import patch

import ipaddress

import keepalived_async_state


IP_CALL = {
    "one service": ["18: dummy12 inet 5.45.202.6/32 scope global dummy12 valid_lft forever preferred_lft forever"],
    "two services": [
        "18: dummy12 inet 5.45.202.6/32 scope global dummy12 valid_lft forever preferred_lft forever",
        "18: dummy12 inet 5.45.202.8/32 scope global dummy12 valid_lft forever preferred_lft forever",
    ],
    "incorrect output": ["18: dummy12 inet ..."],
    "incorrect interface": [
        "18: dummy255 inet 5.45.202.6/32 scope global dummy255 valid_lft forever preferred_lft forever"
    ],
}

KEEPALIVED_OUTPUT = {
    "one service": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 1,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.6,b-100,1",
                "rs": [],
            }
        ],
    },
    "two services": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 1,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.6,b-100,1",
                "rs": [],
            },
            {
                "vip": "5.45.202.8",
                "quorum_state": 1,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.8,b-100,1",
                "rs": [],
            },
        ],
    },
    "one service with incorrect ports count": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 1,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.6,b-100,2",
                "rs": [],
            }
        ],
    },
    "one service with incorrect quorum_call": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 1,
                "quorum_up": "/opt/balancers/scripts/keepalived/quorum-handler-strm-fwmark.sh up",
                "rs": [],
            }
        ],
    },
    "one service with second incorrect quorum_call": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 1,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.6",
                "rs": [],
            }
        ],
    },
    "one service with zero quorum_state": {
        "conf": [
            {
                "vip": "5.45.202.6",
                "quorum_state": 0,
                "quorum_up": "/etc/keepalived/quorum-handler2.sh up 5.45.202.6,b-100,1",
                "rs": [],
            }
        ],
    },
}


class TestKeepalivedAsyncState(TestCase):
    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("one service"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("one service"))
    def test_equal_state(self, *_):
        assert keepalived_async_state.get_async_addresses() == set()

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("two services"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("one service"))
    def test_successful_check(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.8")})

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("one service"))
    @patch(
        "keepalived_async_state.get_keepalived_state",
        return_value=KEEPALIVED_OUTPUT.get("one service with incorrect ports count"),
    )
    def test_incorrect_keepalived_ports_counts(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.6")})

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("one service"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("two services"))
    def test_ip_output(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.8")})

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("two services"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("one service"))
    def test_keepalived_output(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.8")})

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("two services"))
    @patch("keepalived_async_state.get_keepalived_state", return_value={})
    def test_keepalived_failed_output(self, *_):
        assert keepalived_async_state.get_async_addresses() == {
            ipaddress.ip_address("5.45.202.6"),
            ipaddress.ip_address("5.45.202.8"),
        }

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("incorrect output"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("two services"))
    def test_ip_failed_output(self, *_):
        assert keepalived_async_state.get_async_addresses() == {
            ipaddress.ip_address("5.45.202.8"),
            ipaddress.ip_address("5.45.202.6"),
        }

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("incorrect interface"))
    @patch("keepalived_async_state.get_keepalived_state", return_value=KEEPALIVED_OUTPUT.get("two services"))
    def test_ip_incorrect_interface(self, *_):
        assert keepalived_async_state.get_async_addresses() == {
            ipaddress.ip_address("5.45.202.8"),
            ipaddress.ip_address("5.45.202.6"),
        }

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("one service"))
    @patch(
        "keepalived_async_state.get_keepalived_state",
        return_value=KEEPALIVED_OUTPUT.get("one service with incorrect quorum_call"),
    )
    def test_incorrect_quorum_call(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.6")})

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("two services"))
    @patch(
        "keepalived_async_state.get_keepalived_state",
        return_value=KEEPALIVED_OUTPUT.get("one service with second incorrect quorum_call"),
    )
    def test_second_incorrect_quorum_call(self, *_):
        assert keepalived_async_state.get_async_addresses() == {
            ipaddress.ip_address("5.45.202.8"),
            ipaddress.ip_address("5.45.202.6"),
        }

    @patch("tt_main.system.make_cmd_call", return_value=IP_CALL.get("one service"))
    @patch(
        "keepalived_async_state.get_keepalived_state",
        return_value=KEEPALIVED_OUTPUT.get("one service with zero quorum_state"),
    )
    def test_zero_quorum_state(self, *_):
        assert keepalived_async_state.get_async_addresses() == set({ipaddress.ip_address("5.45.202.6")})
