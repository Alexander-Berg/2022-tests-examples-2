from yanetagent import ipnet


class TestIPNet:
    def test_is_ip(self) -> None:
        assert ipnet.is_ip("127.0.0.1")
        assert ipnet.is_ip("::1")
        assert ipnet.is_ip("227.1.2.3")
        assert ipnet.is_ip("2a02:6b8:ff1c:2030::")

        assert not ipnet.is_ip("127.0.0.256")
        assert not ipnet.is_ip("::fffff")
        assert not ipnet.is_ip("2a02:6b8:ff1c:2030::1111:2222:3333:4444")
        assert not ipnet.is_ip("127.0.0.1/32")

    def test_is_ip_or_net(self) -> None:
        assert ipnet.is_ip_or_net("127.0.0.1/32")
        assert ipnet.is_ip_or_net("::1/128")
        assert ipnet.is_ip_or_net("227.1.2.0/24")
        assert ipnet.is_ip_or_net("2a02:6b8:ff1c:2030::/64")
        assert ipnet.is_ip_or_net("2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::")

        assert not ipnet.is_ip_or_net("127.0.0.256")
        assert not ipnet.is_ip_or_net("::fffff")
        assert not ipnet.is_ip_or_net("2a02:6b8:ff1c:2030::1111:2222:3333:4444")
