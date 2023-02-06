from noc.traffic.dns.safedns.dnsl3r.dnsl3r import utils


def test_check_dn_ok():
    assert utils.check_dn("fqdn.test")


def test_check_dn_too_long():
    dn = "a" * 200 + "." + "a" * 200
    assert not utils.check_dn(dn)


def test_check_dn_not_fqdn():
    assert utils.check_dn("not-an-fqdn")


def test_check_dn_too_long_label():
    dn = "a." + "b" * 100
    assert not utils.check_dn(dn)


def test_check_dn_empty_label():
    assert not utils.check_dn("some..test")


def test_check_dn_invalid_characters():
    assert not utils.check_dn("in?valid.test")


def test_parse_ip_list_all():
    iplist = ("192.0.2.15", "192.0.2.20", "2001:db8:ffff::1")
    assert utils.parse_ip_list(iplist) == list(iplist)


def test_parse_ip_list_some_invalid():
    iplist = ("192.0.2.15", "192.0.222", "192.0.2.20")
    assert utils.parse_ip_list(iplist) == ["192.0.2.15", "192.0.2.20"]


def test_parse_ip_list_noting_given():
    assert utils.parse_ip_list(()) == []


def test_parse_ip_list_all_invalid():
    assert utils.parse_ip_list(("192.0.222", "abc.xyz.14")) == []


def test_parse_ip_list_single_address():
    assert utils.parse_ip_list(("2001:db8:ffff::1",)) == ["2001:db8:ffff::1"]
