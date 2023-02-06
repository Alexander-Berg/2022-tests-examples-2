from unittest import mock

import snmpd_ethtool
import snmpd_lib

OID_BASE = ".1.3.6.1.4.1.11069.320.767"


class MockCommand:
    def __init__(self, data):
        self.data = data

    def __call__(self, cmd, exc_if_err=True, use_sudo=False, ok_if_retcode=False, cmd_input=None, timeout=15):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        if cmd in self.data:
            return self.data[cmd]
        raise snmpd_ethtool.CmdException(b"", b"", -1)


IPLINK_TEST_DATA = (
    b"20: swp31: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc ets state UP mode DEFAULT "
    b"group default qlen 1000\\    link/ether 1c:34:da:af:d8:41 brd ff:ff:ff:ff:ff:ff"
)
ETHTOOL_TEST_DATA_SWP31 = b"""NIC statistics:
     a_frames_transmitted_ok: 57271205843
     a_frames_received_ok: 63917145378
     a_frame_check_sequence_errors: 0
     a_alignment_errors: 0
     a_octets_transmitted_ok: 239880508419557
     a_octets_received_ok: 319786790393748
     a_multicast_frames_xmitted_ok: 1066828
     a_broadcast_frames_xmitted_ok: 0
     a_multicast_frames_received_ok: 354545
     a_broadcast_frames_received_ok: 0
     a_in_range_length_errors: 0
     a_out_of_range_length_field: 0
     a_frame_too_long_errors: 0
     a_symbol_error_during_carrier: 0
     a_mac_control_frames_transmitted: 0
     a_mac_control_frames_received: 0
     a_unsupported_opcodes_received: 0
     a_pause_mac_ctrl_frames_received: 0
     a_pause_mac_ctrl_frames_xmitted: 0
     if_in_discards: 0
     if_out_discards: 0
     if_out_errors: 0
     ether_stats_undersize_pkts: 0
     ether_stats_oversize_pkts: 0
     ether_stats_fragments: 0
     ether_pkts64octets: 0
     ether_pkts65to127octets: 14506002870
     ether_pkts128to255octets: 5225389637
     ether_pkts256to511octets: 5029348261
     ether_pkts512to1023octets: 1466420237
     ether_pkts1024to1518octets: 445216089
     ether_pkts1519to2047octets: 330625518
     ether_pkts2048to4095octets: 2074253181
     ether_pkts4096to8191octets: 2147309510
     ether_pkts8192to10239octets: 32692580075
     dot3stats_fcs_errors: 0
     dot3stats_symbol_errors: 0
     dot3control_in_unknown_opcodes: 0
     dot3in_pause_frames: 0
     ecn_marked: 10
     discard_ingress_general: 0
     discard_ingress_policy_engine: 0
     discard_ingress_vlan_membership: 0
     discard_ingress_tag_frame_type: 0
     discard_egress_vlan_membership: 0
     discard_loopback_filter: 0
     discard_egress_general: 0
     discard_egress_hoq: 0
     discard_egress_policy_engine: 0
     discard_ingress_tx_link_down: 0
     discard_egress_stp_filter: 0
     discard_egress_sll: 0
     rx_octets_prio_0: 319786790393748
     rx_frames_prio_0: 63917145378
     tx_octets_prio_0: 251152677
     tx_frames_prio_0: 37447
     rx_pause_prio_0: 0
     rx_pause_duration_prio_0: 0
     tx_pause_prio_0: 0
     tx_pause_duration_prio_0: 0
     rx_octets_prio_1: 0
     rx_frames_prio_1: 0
     tx_octets_prio_1: 2075663330807
     tx_frames_prio_1: 258594768
     rx_pause_prio_1: 0
     rx_pause_duration_prio_1: 0
     tx_pause_prio_1: 0
     tx_pause_duration_prio_1: 0
     rx_octets_prio_2: 0
     rx_frames_prio_2: 0
     tx_octets_prio_2: 101476288988
     tx_frames_prio_2: 12583120
     rx_pause_prio_2: 0
     rx_pause_duration_prio_2: 0
     tx_pause_prio_2: 0
     tx_pause_duration_prio_2: 0
     rx_octets_prio_3: 0
     rx_frames_prio_3: 0
     tx_octets_prio_3: 16352350345145
     tx_frames_prio_3: 6998434690
     rx_pause_prio_3: 0
     rx_pause_duration_prio_3: 0
     tx_pause_prio_3: 0
     tx_pause_duration_prio_3: 0
     rx_octets_prio_4: 0
     rx_frames_prio_4: 0
     tx_octets_prio_4: 221347838755116
     tx_frames_prio_4: 49974991821
     rx_pause_prio_4: 0
     rx_pause_duration_prio_4: 0
     tx_pause_prio_4: 0
     tx_pause_duration_prio_4: 0
     rx_octets_prio_5: 0
     rx_frames_prio_5: 0
     tx_octets_prio_5: 155428
     tx_frames_prio_5: 1586
     rx_pause_prio_5: 0
     rx_pause_duration_prio_5: 0
     tx_pause_prio_5: 0
     tx_pause_duration_prio_5: 0
     rx_octets_prio_6: 0
     rx_frames_prio_6: 0
     tx_octets_prio_6: 0
     tx_frames_prio_6: 0
     rx_pause_prio_6: 0
     rx_pause_duration_prio_6: 0
     tx_pause_prio_6: 0
     tx_pause_duration_prio_6: 0
     rx_octets_prio_7: 0
     rx_frames_prio_7: 0
     tx_octets_prio_7: 2928399454
     tx_frames_prio_7: 26562412
     rx_pause_prio_7: 0
     rx_pause_duration_prio_7: 0
     tx_pause_prio_7: 0
     tx_pause_duration_prio_7: 0
     tc_transmit_queue_tc_0: 0
     tc_no_buffer_discard_uc_tc_0: 0
     tc_transmit_queue_tc_1: 0
     tc_no_buffer_discard_uc_tc_1: 0
     tc_transmit_queue_tc_2: 0
     tc_no_buffer_discard_uc_tc_2: 0
     tc_transmit_queue_tc_3: 0
     tc_no_buffer_discard_uc_tc_3: 0
     tc_transmit_queue_tc_4: 0
     tc_no_buffer_discard_uc_tc_4: 0
     tc_transmit_queue_tc_5: 0
     tc_no_buffer_discard_uc_tc_5: 0
     tc_transmit_queue_tc_6: 0
     tc_no_buffer_discard_uc_tc_6: 0
     tc_transmit_queue_tc_7: 0
     tc_no_buffer_discard_uc_tc_7: 0
     tc_transmit_queue_tc_8: 0
     tc_no_buffer_discard_uc_tc_8: 0
     tc_transmit_queue_tc_9: 0
     tc_no_buffer_discard_uc_tc_9: 0
     tc_transmit_queue_tc_10: 0
     tc_no_buffer_discard_uc_tc_10: 0
     tc_transmit_queue_tc_11: 0
     tc_no_buffer_discard_uc_tc_11: 0
     tc_transmit_queue_tc_12: 0
     tc_no_buffer_discard_uc_tc_12: 0
     tc_transmit_queue_tc_13: 0
     tc_no_buffer_discard_uc_tc_13: 0
     tc_transmit_queue_tc_14: 0
     tc_no_buffer_discard_uc_tc_14: 0
     tc_transmit_queue_tc_15: 0
     tc_no_buffer_discard_uc_tc_15: 0
     transceiver_overheat: 0
"""


@mock.patch("snmpd_ethtool.command")
def test_pass_persist(command_mock):
    command_mock.side_effect = MockCommand(
        {
            "/sbin/ip -o link show": (IPLINK_TEST_DATA, b""),
            "/sbin/ethtool -S swp31": (ETHTOOL_TEST_DATA_SWP31, b""),
        }
    )
    pp = snmpd_lib.PassPersist(OID_BASE)
    ss = snmpd_ethtool.SnmpdPass(pp)
    ss.update()
    assert ss.ports == [(20, 'swp31')]
    assert ss.last_port_data == [
        (
            20,
            'swp31',
            {
                'a_frames_transmitted_ok': '57271205843',
                'a_frames_received_ok': '63917145378',
                'a_frame_check_sequence_errors': '0',
                'a_alignment_errors': '0',
                'a_octets_transmitted_ok': '239880508419557',
                'a_octets_received_ok': '319786790393748',
                'a_multicast_frames_xmitted_ok': '1066828',
                'a_broadcast_frames_xmitted_ok': '0',
                'a_multicast_frames_received_ok': '354545',
                'a_broadcast_frames_received_ok': '0',
                'a_in_range_length_errors': '0',
                'a_out_of_range_length_field': '0',
                'a_frame_too_long_errors': '0',
                'a_symbol_error_during_carrier': '0',
                'a_mac_control_frames_transmitted': '0',
                'a_mac_control_frames_received': '0',
                'a_unsupported_opcodes_received': '0',
                'a_pause_mac_ctrl_frames_received': '0',
                'a_pause_mac_ctrl_frames_xmitted': '0',
                'if_in_discards': '0',
                'if_out_discards': '0',
                'if_out_errors': '0',
                'ether_stats_undersize_pkts': '0',
                'ether_stats_oversize_pkts': '0',
                'ether_stats_fragments': '0',
                'ether_pkts64octets': '0',
                'ether_pkts65to127octets': '14506002870',
                'ether_pkts128to255octets': '5225389637',
                'ether_pkts256to511octets': '5029348261',
                'ether_pkts512to1023octets': '1466420237',
                'ether_pkts1024to1518octets': '445216089',
                'ether_pkts1519to2047octets': '330625518',
                'ether_pkts2048to4095octets': '2074253181',
                'ether_pkts4096to8191octets': '2147309510',
                'ether_pkts8192to10239octets': '32692580075',
                'dot3stats_fcs_errors': '0',
                'dot3stats_symbol_errors': '0',
                'dot3control_in_unknown_opcodes': '0',
                'dot3in_pause_frames': '0',
                'ecn_marked': '10',
                'discard_ingress_general': '0',
                'discard_ingress_policy_engine': '0',
                'discard_ingress_vlan_membership': '0',
                'discard_ingress_tag_frame_type': '0',
                'discard_egress_vlan_membership': '0',
                'discard_loopback_filter': '0',
                'discard_egress_general': '0',
                'discard_egress_hoq': '0',
                'discard_egress_policy_engine': '0',
                'discard_ingress_tx_link_down': '0',
                'discard_egress_stp_filter': '0',
                'discard_egress_sll': '0',
                'rx_octets_prio_0': '319786790393748',
                'rx_frames_prio_0': '63917145378',
                'tx_octets_prio_0': '251152677',
                'tx_frames_prio_0': '37447',
                'rx_pause_prio_0': '0',
                'rx_pause_duration_prio_0': '0',
                'tx_pause_prio_0': '0',
                'tx_pause_duration_prio_0': '0',
                'rx_octets_prio_1': '0',
                'rx_frames_prio_1': '0',
                'tx_octets_prio_1': '2075663330807',
                'tx_frames_prio_1': '258594768',
                'rx_pause_prio_1': '0',
                'rx_pause_duration_prio_1': '0',
                'tx_pause_prio_1': '0',
                'tx_pause_duration_prio_1': '0',
                'rx_octets_prio_2': '0',
                'rx_frames_prio_2': '0',
                'tx_octets_prio_2': '101476288988',
                'tx_frames_prio_2': '12583120',
                'rx_pause_prio_2': '0',
                'rx_pause_duration_prio_2': '0',
                'tx_pause_prio_2': '0',
                'tx_pause_duration_prio_2': '0',
                'rx_octets_prio_3': '0',
                'rx_frames_prio_3': '0',
                'tx_octets_prio_3': '16352350345145',
                'tx_frames_prio_3': '6998434690',
                'rx_pause_prio_3': '0',
                'rx_pause_duration_prio_3': '0',
                'tx_pause_prio_3': '0',
                'tx_pause_duration_prio_3': '0',
                'rx_octets_prio_4': '0',
                'rx_frames_prio_4': '0',
                'tx_octets_prio_4': '221347838755116',
                'tx_frames_prio_4': '49974991821',
                'rx_pause_prio_4': '0',
                'rx_pause_duration_prio_4': '0',
                'tx_pause_prio_4': '0',
                'tx_pause_duration_prio_4': '0',
                'rx_octets_prio_5': '0',
                'rx_frames_prio_5': '0',
                'tx_octets_prio_5': '155428',
                'tx_frames_prio_5': '1586',
                'rx_pause_prio_5': '0',
                'rx_pause_duration_prio_5': '0',
                'tx_pause_prio_5': '0',
                'tx_pause_duration_prio_5': '0',
                'rx_octets_prio_6': '0',
                'rx_frames_prio_6': '0',
                'tx_octets_prio_6': '0',
                'tx_frames_prio_6': '0',
                'rx_pause_prio_6': '0',
                'rx_pause_duration_prio_6': '0',
                'tx_pause_prio_6': '0',
                'tx_pause_duration_prio_6': '0',
                'rx_octets_prio_7': '0',
                'rx_frames_prio_7': '0',
                'tx_octets_prio_7': '2928399454',
                'tx_frames_prio_7': '26562412',
                'rx_pause_prio_7': '0',
                'rx_pause_duration_prio_7': '0',
                'tx_pause_prio_7': '0',
                'tx_pause_duration_prio_7': '0',
                'tc_transmit_queue_tc_0': '0',
                'tc_no_buffer_discard_uc_tc_0': '0',
                'tc_transmit_queue_tc_1': '0',
                'tc_no_buffer_discard_uc_tc_1': '0',
                'tc_transmit_queue_tc_2': '0',
                'tc_no_buffer_discard_uc_tc_2': '0',
                'tc_transmit_queue_tc_3': '0',
                'tc_no_buffer_discard_uc_tc_3': '0',
                'tc_transmit_queue_tc_4': '0',
                'tc_no_buffer_discard_uc_tc_4': '0',
                'tc_transmit_queue_tc_5': '0',
                'tc_no_buffer_discard_uc_tc_5': '0',
                'tc_transmit_queue_tc_6': '0',
                'tc_no_buffer_discard_uc_tc_6': '0',
                'tc_transmit_queue_tc_7': '0',
                'tc_no_buffer_discard_uc_tc_7': '0',
                'tc_transmit_queue_tc_8': '0',
                'tc_no_buffer_discard_uc_tc_8': '0',
                'tc_transmit_queue_tc_9': '0',
                'tc_no_buffer_discard_uc_tc_9': '0',
                'tc_transmit_queue_tc_10': '0',
                'tc_no_buffer_discard_uc_tc_10': '0',
                'tc_transmit_queue_tc_11': '0',
                'tc_no_buffer_discard_uc_tc_11': '0',
                'tc_transmit_queue_tc_12': '0',
                'tc_no_buffer_discard_uc_tc_12': '0',
                'tc_transmit_queue_tc_13': '0',
                'tc_no_buffer_discard_uc_tc_13': '0',
                'tc_transmit_queue_tc_14': '0',
                'tc_no_buffer_discard_uc_tc_14': '0',
                'tc_transmit_queue_tc_15': '0',
                'tc_no_buffer_discard_uc_tc_15': '0',
                'transceiver_overheat': '0',
            },
        )
    ]

    assert pp.pending == {
        '1.20': {'type': 'STRING', 'value': 'swp31'},
        '2.1': {'type': 'STRING', 'value': 'ifname'},
        '2.2': {'type': 'STRING', 'value': 'ethtool counter name'},
        '2.4': {'type': 'STRING', 'value': 'HwIfInErrors'},
        '2.5': {'type': 'STRING', 'value': 'rx_crc_errors'},
        '2.6': {'type': 'STRING', 'value': 'dropped_smbus'},
        '2.7': {'type': 'STRING', 'value': 'tc_no_buffer_discard_uc_tc'},
        '2.8': {'type': 'STRING', 'value': 'tc_no_buffer_discard_uc_tc_sum'},
        '2.9': {'type': 'STRING', 'value': 'if_out_discards'},
        '2.10': {'type': 'STRING', 'value': 'tc_transmit_queue_tc'},
        '2.11': {'type': 'STRING', 'value': 'tc_transmit_queue_tc_sum'},
        '7.20.0': {'type': 'Counter64', 'value': '0'},
        '7.20.1': {'type': 'Counter64', 'value': '0'},
        '7.20.10': {'type': 'Counter64', 'value': '0'},
        '7.20.11': {'type': 'Counter64', 'value': '0'},
        '7.20.12': {'type': 'Counter64', 'value': '0'},
        '7.20.13': {'type': 'Counter64', 'value': '0'},
        '7.20.14': {'type': 'Counter64', 'value': '0'},
        '7.20.15': {'type': 'Counter64', 'value': '0'},
        '7.20.2': {'type': 'Counter64', 'value': '0'},
        '7.20.3': {'type': 'Counter64', 'value': '0'},
        '7.20.4': {'type': 'Counter64', 'value': '0'},
        '7.20.5': {'type': 'Counter64', 'value': '0'},
        '7.20.6': {'type': 'Counter64', 'value': '0'},
        '7.20.7': {'type': 'Counter64', 'value': '0'},
        '7.20.8': {'type': 'Counter64', 'value': '0'},
        '7.20.9': {'type': 'Counter64', 'value': '0'},
        '8.20': {'type': 'Counter64', 'value': '0'},
        '9.20': {'type': 'Counter64', 'value': '0'},
        '10.20.0': {'type': 'Counter64', 'value': '0'},
        '10.20.1': {'type': 'Counter64', 'value': '0'},
        '10.20.10': {'type': 'Counter64', 'value': '0'},
        '10.20.11': {'type': 'Counter64', 'value': '0'},
        '10.20.12': {'type': 'Counter64', 'value': '0'},
        '10.20.13': {'type': 'Counter64', 'value': '0'},
        '10.20.14': {'type': 'Counter64', 'value': '0'},
        '10.20.15': {'type': 'Counter64', 'value': '0'},
        '10.20.2': {'type': 'Counter64', 'value': '0'},
        '10.20.3': {'type': 'Counter64', 'value': '0'},
        '10.20.4': {'type': 'Counter64', 'value': '0'},
        '10.20.5': {'type': 'Counter64', 'value': '0'},
        '10.20.6': {'type': 'Counter64', 'value': '0'},
        '10.20.7': {'type': 'Counter64', 'value': '0'},
        '10.20.8': {'type': 'Counter64', 'value': '0'},
        '10.20.9': {'type': 'Counter64', 'value': '0'},
        '11.20': {'type': 'Counter64', 'value': '0'},
    }


def test_snmpd_lib_summer():
    maxint = 2 ** 64 - 1
    summer = snmpd_lib.Summer()
    key = "ololo"
    indexes = [0, 1, 2]
    for index in indexes:
        summer.add(key, index, 1)
    assert summer.get(key) == 0

    for index in indexes:
        summer.add(key, index, 10)
    assert summer.get(key) == 27

    summer.add(key, 0, 10)
    summer.add(key, 1, maxint - 40)
    summer.add(key, 2, 10)
    assert summer.get(key) == 18446744073709551592

    summer.add(key, 0, 0)
    summer.add(key, 1, maxint - 40)
    summer.add(key, 2, 100)
    assert summer.get(key) == 67

    summer.add(key, 0, 0)
    summer.add(key, 1, maxint - 20)
    summer.add(key, 2, 0)
    assert summer.get(key) == 87
