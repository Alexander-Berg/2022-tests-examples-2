from unittest.mock import patch
from monstatus import query_juggler
from ppsc import KEEPALIVED_REQUIRED_J_CHECKS


def test_query_juggler_ok():
    data = [
        '[',
        '    {',
        '        "created": "Mon Feb  1 14:26:16 2021",',
        '        "description": "ok",',
        '        "service": "bird_proto",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:17 2021",',
        '        "description": "ok",',
        '        "service": "check_tun",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:21 2021",',
        '        "description": "ok",',
        '        "service": "tunnel_interfaces",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    }',
        ']'
    ]
    with patch("monstatus.make_cmd_call", return_value=data):
        result, message = query_juggler(KEEPALIVED_REQUIRED_J_CHECKS)
    assert result == 0
    assert not message


def test_query_juggler_warn_and_crit():
    data = [
        '[',
        '    {',
        '        "created": "Mon Feb  1 14:26:16 2021",',
        '        "description": "ok",',
        '        "service": "bird_proto",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:43:31 2021",',
        '        "description": "announces disabled?",',
        '        "service": "svc_announced",',
        '        "status": "WARN"',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:17 2021",',
        '        "description": "/usr/sbin/check-tun pid not found",',
        '        "service": "check_tun",',
        '        "status": "CRIT",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:21 2021",',
        '        "description": "ok",',
        '        "service": "tunnel_interfaces",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    }',
        ']'
    ]
    with patch("monstatus.make_cmd_call", return_value=data):
        result, message = query_juggler(KEEPALIVED_REQUIRED_J_CHECKS)
    assert result == 1
    assert message == ("CRIT: check_tun (/usr/sbin/check-tun pid not found); "
                       "WARN: svc_announced (announces disabled?)")


def test_query_juggler_warn():
    data = [
        '[',
        '    {',
        '        "created": "Mon Feb  1 14:26:16 2021",',
        '        "description": "ok",',
        '        "service": "bird_proto",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:43:31 2021",',
        '        "description": "announces disabled?",',
        '        "service": "svc_announced",',
        '        "status": "WARN"',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:21 2021",',
        '        "description": "ok",',
        '        "service": "tunnel_interfaces",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    }',
        ']'
    ]
    with patch("monstatus.make_cmd_call", return_value=data):
        result, message = query_juggler(KEEPALIVED_REQUIRED_J_CHECKS)
    assert result == 0
    assert message == "WARN: svc_announced (announces disabled?)"


def test_query_juggler_crit():
    data = [
        '[',
        '    {',
        '        "created": "Mon Feb  1 14:26:16 2021",',
        '        "description": "ok",',
        '        "service": "bird_proto",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:17 2021",',
        '        "description": "/usr/sbin/check-tun pid not found",',
        '        "service": "check_tun",',
        '        "status": "CRIT",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:21 2021",',
        '        "description": "ok",',
        '        "service": "tunnel_interfaces",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    }',
        ']'
    ]
    with patch("monstatus.make_cmd_call", return_value=data):
        result, message = query_juggler(KEEPALIVED_REQUIRED_J_CHECKS)
    assert result == 1
    assert message == "CRIT: check_tun (/usr/sbin/check-tun pid not found)"


def test_query_juggler_crit_we_dont_care_about():
    data = [
        '[',
        '    {',
        '        "created": "Mon Feb  1 14:26:16 2021",',
        '        "description": "ok",',
        '        "service": "bird_proto",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:17 2021",',
        '        "description": "yandex.net is outdated",',
        '        "service": "bind_zones",',
        '        "status": "CRIT",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    },',
        '    {',
        '        "created": "Mon Feb  1 14:26:21 2021",',
        '        "description": "ok",',
        '        "service": "tunnel_interfaces",',
        '        "status": "OK",',
        '        "tags": [',
        '            "bundle-monitoring"',
        '        ]',
        '    }',
        ']'
    ]
    with patch("monstatus.make_cmd_call", return_value=data):
        result, message = query_juggler(KEEPALIVED_REQUIRED_J_CHECKS)
    assert result == 0
    assert not message
