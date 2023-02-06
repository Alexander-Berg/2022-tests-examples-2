from noc.racktables.netmap.lib.access_point_parsing import (
    parse_access_point_info,
    parse_access_point_summary,
    parse_wlan_summary,
    WlanName,
)


def test_parse_wlan_summary_regexp():
    example = r'''
Number of WLANs.................................. 14

WLAN ID  WLAN Profile Name / SSID               Status    Interface Name        PMIPv6 Mobility
-------  -------------------------------------  --------  --------------------  ---------------
2        Guests PSK / Guests                    Enabled   igroup.natguest       none
    '''
    assert parse_wlan_summary(example) == {'2': WlanName('Guests PSK', 'Guests')}


def test_parse_access_point_summary_regexp():
    ap_summary_example = r'''
Number of APs.................................... 537

Global AP User Name.............................. root
Global AP Dot1x User Name........................ Not Configured

AP Name                         Slots  AP Model              Ethernet MAC       Location              Country     IP Address       Clients  DSE Location
------------------------------  -----  --------------------  -----------------  --------------------  ----------  ---------------  -------  --------------
red2-53w11                      2      AIR-CAP3602E-R-K9      6c:41:6a:b2:07:b9  default location      RU          172.27.75.109    7        [0 ,0 ,0 ]
    '''

    assert parse_access_point_summary(ap_summary_example) == ['red2-53w11']


def test_wlan_info():
    wlan_info_example = r'''
Site Name........................................ RedRose.Mamontov
Site Description................................. <none>

WLAN ID          Interface          BSSID                             ATF Override         ATF Policy ID         ATF Policy Name
-------         -----------        --------------------------       --------------         --------------       --------------
3               igroup.yandex        e4:aa:5d:e3:0c:7f                      n/a             n/a                      n/a
    '''
    assert parse_access_point_info(wlan_info_example) == {'3': 'E4AA5DE30C7F'}
