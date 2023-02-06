from comocutor_contrib.lib import table_parser, TableType, parse_rows_index, split_table_by_indexes


def test_parse_table():
    table = """                                 Sent       Rcvd
    Prefixes Current:             817          0
    Prefixes Total:              1734          0
    Implicit Withdraw:            825          0
    Explicit Withdraw:            884          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0"""
    assert table_parser(table, TableType.V1) == {'Prefixes Current': {'Sent': '817', 'Rcvd': '0'},
                                                 'Prefixes Total': {'Sent': '1734', 'Rcvd': '0'},
                                                 'Implicit Withdraw': {'Sent': '825', 'Rcvd': '0'},
                                                 'Explicit Withdraw': {'Sent': '884', 'Rcvd': '0'},
                                                 'Used as bestpath': {'Sent': 'n/a', 'Rcvd': '0'},
                                                 'Used as multipath': {'Sent': 'n/a', 'Rcvd': '0'}}
    table = """    Item                  Packets                Bytes           pps           bps
     Matched                 27590            217582509             0             0
     Passed                  27590            217582509             0             0
     Dropped                     0                    0             0             0
     Filter                      0                    0             0             0
     CAR                         0                    0             0             0"""
    exp = {"Matched": {"Packets": "27590", "Bytes": "217582509", "pps": "0", "bps": "0"},
           "Passed": {"Packets": "27590", "Bytes": "217582509", "pps": "0", "bps": "0"},
           "Dropped": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"},
           "Filter": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"},
           "CAR": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"}}
    assert table_parser(table, TableType.V1_1, row_name_separator=" ") == exp

    table = """Destination  : ::                                      PrefixLength : 0
NextHop      : 2A02:6B8:B010:8004::1                   Preference   : 60
Cost         : 0                                       Protocol     : Static
RelayNextHop : 2A02:6B8:B010:8004::1                   TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : RD"""
    exp = {"Destination": "::", "PrefixLength": "0", "NextHop": "2A02:6B8:B010:8004::1", "Preference": "60",
           "Cost": "0", "Protocol": "Static", "RelayNextHop": "2A02:6B8:B010:8004::1", "TunnelID": "0x0",
           "Interface": "MEth0/0/0", "Flags": "RD"}
    assert table_parser(table, TableType.V2, row_name_separator=":") == exp

    table = """Destination/Mask                             Protocol
Nexthop                                      Interface
 ::/0                                        Static
  2A02:6B8:B010:8004::1                      MEth0/0/0
 ::1/128                                     Direct
  ::1                                        InLoopBack0
 ::FFFF:127.0.0.0/104                        Direct
  ::FFFF:127.0.0.1                           InLoopBack0
 ::FFFF:127.0.0.1/128                        Direct
  ::1                                        InLoopBack0
 64:FF9B::/64                                Static
  2A02:6B8:B010:8004::1                      MEth0/0/0
 64:FF9B::/96                                Static
  2A02:6B8:B010:8004::1                      MEth0/0/0
 2A02::1/128                                 Direct
  ::1                                        LoopBack1
 2A02:6B8::/96                               Static
  2A02:6B8:B010:8004::1                      MEth0/0/0
 2A02:6B8:B010:8004::/64                     Direct
  2A02:6B8:B010:8004::7850                   MEth0/0/0
 2A02:6B8:B010:8004::7850/128                Direct
  ::1                                        MEth0/0/0
 FE80::/10                                   Direct
  ::                                         NULL0
    """
    exp = [{"Destination/Mask": "::/0", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "::1/128", "Protocol": "Direct", "Nexthop": "::1", "Interface": "InLoopBack0"},
           {"Destination/Mask": "::FFFF:127.0.0.0/104", "Protocol": "Direct", "Nexthop": "::FFFF:127.0.0.1",
            "Interface": "InLoopBack0"},
           {"Destination/Mask": "::FFFF:127.0.0.1/128", "Protocol": "Direct", "Nexthop": "::1",
            "Interface": "InLoopBack0"},
           {"Destination/Mask": "64:FF9B::/64", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "64:FF9B::/96", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "2A02::1/128", "Protocol": "Direct", "Nexthop": "::1", "Interface": "LoopBack1"},
           {"Destination/Mask": "2A02:6B8::/96", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "2A02:6B8:B010:8004::/64", "Protocol": "Direct", "Nexthop": "2A02:6B8:B010:8004::7850",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "2A02:6B8:B010:8004::7850/128", "Protocol": "Direct", "Nexthop": "::1",
            "Interface": "MEth0/0/0"},
           {"Destination/Mask": "FE80::/10", "Protocol": "Direct", "Nexthop": "::", "Interface": "NULL0"}]
    assert table_parser(table, TableType.V3, row_name_separator=None, params={"cols": 2}) == exp


def test_parse_rows_index():
    res = parse_rows_index(
        " Destination/PrefixLength                     Nexthop                                  Flag  Interface                  TunnelID")
    exp = [('Destination/PrefixLength', (0, 46)), ('Nexthop', (46, 87)), ('Flag', (87, 93)), ('Interface', (93, 120)),
           ('TunnelID', (120, 128))]
    assert res == exp


def test_split_table_by_indexes():
    indexes = [('Destination/PrefixLength', (0, 46)), ('Nexthop', (46, 87)), ('Flag', (87, 93)),
               ('Interface', (93, 120)), ('TunnelID', (120, 128))]
    res = split_table_by_indexes(indexes,
                                 " 2A02:6B8::1/128                              2A02:6B8:0:1A6A::BA3A                    DGHU  Vlanif801                   -         ")
    exp = [{'Destination/PrefixLength': '2A02:6B8::1/128', 'Nexthop': '2A02:6B8:0:1A6A::BA3A', 'Flag': 'DGHU',
            'Interface': 'Vlanif801', 'TunnelID': '-'}]
    assert res == exp
    res = split_table_by_indexes(indexes,
                                 (
                                     " 2A02:6B8::1/128                              2A02:6B8:0:1A6A::BA3A                    DGHU  Vlanif801                   -         \n"
                                     "                                              2A02:6B8:0:2A6A::BA1A                    DGHU  Vlanif801                   -         \n"
                                     " 2A02:1B8::2/128                              2A02:6B8:0:2A6A::BA1A                    DGHU  Vlanif801                   -"),
                                 empty_replace_last=True)
    # третья строка неполная
    exp = [{'Destination/PrefixLength': '2A02:6B8::1/128', 'Nexthop': '2A02:6B8:0:1A6A::BA3A', 'Flag': 'DGHU',
            'Interface': 'Vlanif801', 'TunnelID': '-'},
           {'Destination/PrefixLength': '2A02:6B8::1/128', 'Nexthop': '2A02:6B8:0:2A6A::BA1A', 'Flag': 'DGHU',
            'Interface': 'Vlanif801', 'TunnelID': '-'},
           {'Destination/PrefixLength': '2A02:1B8::2/128', 'Nexthop': '2A02:6B8:0:2A6A::BA1A', 'Flag': 'DGHU',
            'Interface': 'Vlanif801', 'TunnelID': '-'}]
    assert res == exp
