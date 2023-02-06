import ipaddress
import random
from unittest.mock import patch

from links_at_max_speed import check_links_at_max_speed, find_interfaces
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS


def gen_ip_addr_output(links):
    """Generates fake 'ip -o address' output for mocking purpose.
    Argument: links - dict with {"interface_name": "af"} format; af - is
    address family, which addresses must exist on interface. Accept values:
        - v4: for IPv4
        - v6: for IPv6
        - both: for IPv4 and IPv6
        - ll: only link-local IPv6 address
    Returns: multiline string resembling 'ip -o address' output."""
    def random_address(family):
        """Helper function, that generates random IP address.
        Argument: family - either 'v4' or 'v6'; address from usch family will
        be generated.
        Returns: string with IPv4 or IPv6 address."""
        if family == "v4":
            return ipaddress.IPv4Address._string_from_ip_int(
                random.randint(0, ipaddress.IPv4Address._ALL_ONES))
        elif family == "v6":
            return ipaddress.IPv6Address._string_from_ip_int(
                random.randint(0, ipaddress.IPv6Address._ALL_ONES))

    def gen_addr_string(num, link, family):
        """Helper function, which produce string, appropriate to mock 'ip -o
        address' output.
        Arguments:
            * num - interface index, first columnt in output
            * link - interface name
            * family - address-family, see gen_ip_addr_output"""
        const_part = "\\\t\tvalid_lft forever preferred_lft forever"
        if family == "v4":
            address = random_address("v4")
            dyn_part = "{}: {}\tinet {}/24 brd {} scope global {} ".format(
                num, link, address, address, link)
        elif family == "v6":
            address = random_address("v6")
            dyn_part = "{}: {}\tinet6 {}/64 scope global ".format(
                num, link, address)
        elif family == "ll":
            address = random_address("v6")
            first_colon = address.index(":")
            address = "fe80" + address[first_colon:]
            dyn_part = "{}: {}\tinet6 {}/64 scope link ".format(
                num, link, address)
        return dyn_part + const_part

    random.seed(44)
    output_string = ""
    for num, link in enumerate(links):
        if links[link] == "both":
            output_string += gen_addr_string(num, link, "v4")
            output_string += gen_addr_string(num, link, "v6")
            output_string += gen_addr_string(num, link, "ll")
        elif links[link] == "v4":
            output_string += gen_addr_string(num, link, "v4")
        elif links[link] == "v6":
            output_string += gen_addr_string(num, link, "v6")
            output_string += gen_addr_string(num, link, "ll")
        elif links[link] == "ll":
            output_string += gen_addr_string(num, link, "ll")
    return output_string


def gen_ethtool_output(interface,
                       max_speed,
                       operating_speed,
                       virtual=False,
                       link=True):
    """Generates fake 'ethtool $INT_NAME' output for mocking purpose.
    Arguments:
        * interface - interface name
        * max_speed - integer, which defines maximum speed of this interface in
            megabits per second, i.e. 10000
        * operating_speed - same as max_speed, but defines speed on which
            interface operates at the moment
        * virtual (defaults to False) - boolean, if True - this interface is
            not physical, i.e. loopback, subinterface, etc...
        * link (defaults to True) - boolean, if True - link is operational at
            the moment
    Returns: multiline string, resembling 'ethtool $INT_NAME' output."""
    skel = """Settings for {}:
        Supported ports: [{}]
        Supported link modes:{}
        Supported pause frame use: Symmetric
        Supports auto-negotiation: Yes
        Supported FEC modes: Not reported
        Advertised link modes:{}
        Advertised pause frame use: No
        Advertised auto-negotiation: Yes
        Advertised FEC modes: Not reported
        Speed: {}Mb/s
        Duplex: Full
        Port: Direct Attach Copper
        PHYAD: 0
        Transceiver: internal
        Auto-negotiation: on
Cannot get wake-on-lan settings: Operation not permitted
        Current message level: 0x00000004 (4)
        link
        Link detected: """
    if link:
        skel += "yes"
    else:
        skel += "no"

    if max_speed == 1000:
        link_modes = ("\t10baseT/Half 10baseT/Full\n\t\t\t100baseT/Half "
                      "100baseT/Full\n\t\t\t1000baseT/Full")
    elif max_speed == 10000:
        link_modes = "\t10000baseT/Full"
    elif max_speed == 25000:
        link_modes = ("\t1000baseKX/Full\n\t\t\t10000baseKR/Full\n\t\t\t"
                      "25000baseCR/Full\n\t\t\t25000baseKR/Full\n\t\t\t"
                      "25000baseSR/Full")
    if virtual:
        supported_ports = " "
    else:
        supported_ports = " BACKPLANE "
    return skel.format(interface, supported_ports, link_modes, link_modes,
                       operating_speed)


def test_two_links_found():
    with patch("links_at_max_speed.make_cmd_call",
               return_value=gen_ip_addr_output({
                   "eth0": "both",
                   "eth1": "both",
                   "eth0.1601": "ll",
                   "eth1.1601": "ll",
                   "dummy0": "ll",
                   "ip6tnl0": "ll"
               })):
        interfaces = find_interfaces()
        assert len(interfaces) == 2
        assert "eth0" in interfaces and "eth1" in interfaces


def test_consistent_name_links_found():
    with patch("links_at_max_speed.make_cmd_call",
               return_value=gen_ip_addr_output({
                   "enp1s0": "both",
                   "enp2s0": "both",
                   "enp2s0.1234": "both",
                   "eno1": "both",
                   "eno1.1234": "both",
                   "ens1f0np0": "both",
                   "ens1f1np1": "both",
                   "ens1f1np1.1234": "both",
                   "ens1f0": "both",
                   "ens1f1": "both",
                   "ens1f1.1234": "both",
               })):
        interfaces = find_interfaces()
        expected_interfaces = [
            "enp1s0", "enp2s0", "eno1", "ens1f0np0", "ens1f1np1", "ens1f0",
            "ens1f1"
        ]

        assert set(interfaces) == set(expected_interfaces)


def test_virtual_links_not_found():
    with patch("links_at_max_speed.make_cmd_call",
               return_value=gen_ip_addr_output({
                   "dummy0": "ll",
                   "ip6tnl0": "ll",
                   "virbr0": "both",
                   "macvtap0": "both",
                   "macvtap1": "both",
               })):
        interfaces = find_interfaces()
        assert interfaces == []


def test_one_link_found():
    with patch("links_at_max_speed.make_cmd_call",
               return_value=gen_ip_addr_output({
                   "eth0": "both",
                   "eth1": "ll",
                   "eth2": "ll",
                   "eth3": "ll",
                   "eth0.1601": "ll",
                   "eth1.1601": "ll",
                   "dummy0": "ll",
                   "ip6tnl0": "ll"
               })):
        assert find_interfaces() == ["eth0"]


def test_one_link_ok():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      return_value=gen_ethtool_output("eth0", 25000, 25000))
    patch_one.start()
    patch_two.start()
    assert check_links_at_max_speed()[0] == OK_STATUS


def test_two_links_ok():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0", "eth1"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      side_effect=[
                          gen_ethtool_output("eth0", 25000, 25000),
                          gen_ethtool_output("eth1", 25000, 25000)
                      ])
    patch_one.start()
    patch_two.start()
    assert check_links_at_max_speed()[0] == OK_STATUS


def test_one_link_bad():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      return_value=gen_ethtool_output("eth0", 25000, 10000))
    patch_one.start()
    patch_two.start()
    result = check_links_at_max_speed()
    assert result[0] == CRIT_STATUS
    assert "eth0 operates on 10 Gb/s, can do 25" in result[1]


def test_two_links_bad():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0", "eth1"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      side_effect=[
                          gen_ethtool_output("eth0", 25000, 10000),
                          gen_ethtool_output("eth1", 10000, 1000)
                      ])
    patch_one.start()
    patch_two.start()
    result = check_links_at_max_speed()
    assert result[0] == CRIT_STATUS
    assert "eth0 operates on 10 Gb/s, can do 25" in result[1]
    assert "eth1 operates on 1 Gb/s, can do 10" in result[1]


def test_one_link_ok_one_bad():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0", "eth1"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      side_effect=[
                          gen_ethtool_output("eth0", 25000, 25000),
                          gen_ethtool_output("eth1", 25000, 10000)
                      ])
    patch_one.start()
    patch_two.start()
    result = check_links_at_max_speed()
    assert result[0] == CRIT_STATUS
    assert "eth1 operates on 10 Gb/s, can do 25" in result[1]
    assert "eth0" not in result[1]


def test_ethtool_output_error():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0", "eth1"])
    patch_two = patch("links_at_max_speed.make_cmd_call", return_value="")
    patch_one.start()
    patch_two.start()
    result = check_links_at_max_speed()
    assert result[0] == CRIT_STATUS
    assert "can't parse" in result[1]


def test_virtual_machine():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      return_value=gen_ethtool_output("eth0",
                                                      10000,
                                                      1000,
                                                      virtual=True))
    patch_one.start()
    patch_two.start()
    assert check_links_at_max_speed()[0] == OK_STATUS


def test_two_links_one_down():
    patch_one = patch("links_at_max_speed.find_interfaces",
                      return_value=["eth0", "eth1"])
    patch_two = patch("links_at_max_speed.make_cmd_call",
                      side_effect=[
                          gen_ethtool_output("eth0", 25000, 25000),
                          gen_ethtool_output("eth1", 25000, 10000, link=False)
                      ])
    patch_one.start()
    patch_two.start()
    assert check_links_at_max_speed()[0] == OK_STATUS
