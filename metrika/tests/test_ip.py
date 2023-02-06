import pytest

from metrika.pylib.ip import validate_ip_to_network, ip_to_bytes, _ip_to_bytes


mask_checks = [
    ('2a02:6b8:c09:1199:0:660:8f96:a57a', '2a02:6b8:c00::660:0:0', 'ffff:ffff:ff00:0:ffff:ffff::', True),
    ('2a02:6b8:1c09:1199:0:660:8f96:a57a', '2a02:6b8:c00::660:0:0', 'ffff:ffff:ff00:0:ffff:ffff::', False),
    ('2a02:6b8:c09:1199:a:660:8f96:a57a', '2a02:6b8:c00::660:0:0', 'ffff:ffff:ff00:0:ffff:ffff::', False),
    ('2a02:6b8:0:807:acd::442', '2a02:6b8:0:807::', 'ffff:ffff:ffff:ffff::', True),
    ('2a02:6b8:1:807:acd::442', '2a02:6b8:0:807::', 'ffff:ffff:ffff:ffff::', False),
    ('2a02:6b8:b011:3029:a:54::1', '2a02:6b8:b011:3000::', 'ffff:ffff:ffff:ff00::', True),
    ('2a02:6b8:b011:3129:a:54::1', '2a02:6b8:b011:3000::', 'ffff:ffff:ffff:ff00::', False),
    ('178.154.224.127', '178.154.224.64', '255.255.255.192', True),
    ('178.154.224.128', '178.154.224.64', '255.255.255.192', False),
]

bytes_checks = [
    ('2a02:6b8:c09:1199:0:660:8f96:a57a', b'*\x02\x06\xb8\x0c\t\x11\x99\x00\x00\x06`\x8f\x96\xa5z'),
    ('178.154.224.100', b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xb2\x9a\xe0d'),
]


@pytest.mark.parametrize('ip,net,mask,result', mask_checks)
def test_mask(ip, net, mask, result):
    assert validate_ip_to_network(ip, net, mask) == result


@pytest.mark.parametrize('ip,expected', bytes_checks)
def test_bytes(ip, expected):
    b = ip_to_bytes(ip)
    assert len(b) == 16
    assert b == expected

    old = _ip_to_bytes(ip)
    assert b == old
