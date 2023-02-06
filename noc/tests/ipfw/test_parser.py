from yanetagent.ipfw.parser import parse


class TestParser:
    def test_parse_basic(self):
        text = r"""
        add allow tcp from any to any 22
        """
        parse(text)

    def test_parse_port_sequence(self):
        text = r"""
        add allow tcp from any to any 80,443
        """
        parse(text)

    def test_parse_port_range(self):
        text = r"""
        add allow tcp from any to any 5000-65535
        """
        parse(text)

    def test_parse_multiline(self):
        text = r"""
        add allow tcp from any to any 22
        add allow tcp from any to any 80,443
        add allow tcp from any to any 1000-1024
        """
        parse(text)

    def test_parse_multiple_protocols(self):
        text = r"""
        add allow { tcp or udp } from any to any 5000-65535
        """
        parse(text)

    def test_parse_multiple_targets(self):
        text = r"""
        add allow tcp from 127.0.0.1 to { 192.168.0.1 or 172.0.0.1/24 } 80
        """
        parse(text)

    def test_parse_multiple_targets_without_spaces(self):
        text = r"""
        add allow tcp from 127.0.0.1 to {192.168.0.1 or 172.0.0.1/24} 80
        """
        parse(text)

    def test_parse_macro(self):
        text = r"""
        add allow tcp from 127.0.0.1 to { _CLOUDINFRANETS_ } 80
        """
        parse(text)

    def test_parse_hostname(self):
        text = r"""
        add allow tcp from 127.0.0.1 to { sas-packfw01.tst.net.yandex.net } 80
        """
        parse(text)

    def test_out_option(self):
        text = r"""
        add allow tcp from any to any 80 out
        """
        parse(text)

    def test_via_option(self):
        text = r"""
        add allow tcp from any to any 80 out via vlan659
        """
        parse(text)

    def test_icmp_type_option(self):
        text = r"""
        add allow ip from any to any icmptype 11
        """
        parse(text)

    def test_icmp_types_option(self):
        text = r"""
        add allow ip from any to any icmptypes 1,2,3,4,128,135,136
        """
        parse(text)

    def test_icmp6_types_option(self):
        text = r"""
        add allow ip from any to any icmp6types 1,2,3,4,128,135,136
        """
        parse(text)

    def test_frag_option(self):
        text = r"""
        add allow ip from any to any frag
        """
        parse(text)

    def test_src_port_option(self):
        text = r"""
        add allow tcp from me to { _ROUTERSNETS_ or _VRFCONNECT_ } src-port 179
        """
        parse(text)

    def test_dst_port_option(self):
        text = r"""
        add allow udp from { _ROUTERSNETS_ or _VRFCONNECT_ } to { _ROUTERSNETS_ or _VRFCONNECT_ } dst-port 3784,4784
        """
        parse(text)

    def test_keep_state_option(self):
        text = r"""
        add allow icmp from me to any icmptypes 8 out keep-state
        """
        parse(text)

    def test_tcp_flags_option(self):
        text = r"""
        add skipto :HBF_SKIP_CHECKSTATE tcp from any to any tcpflags syn,!ack
        """
        parse(text)

    def test_setup_option(self):
        text = r"""
        add skipto :HBF_SKIP_CHECKSTATE tcp from any to any setup
        """
        parse(text)

    def test_proto_option(self):
        text = r"""
        add allow ip from { _YANDEXNETS_ } to { _TUN64_ANYCAST_ } proto ipencap in
        add allow ip from { _IPIP_SOURCES_ } to { _YANDEXNETS6_ } proto ipv6 out
        add allow tag 653 ip4 from { 172.20.0.0/16 } to { _NOCMGMTSRV_ } { proto tcp or proto icmp or proto udp }
        """
        parse(text)

    def test_antispoof_option(self):
        text = r"""
        add allow tcp from 10.0.0.0/8 to 10.0.0.0/8 80 in antispoof
        """
        parse(text)

    def test_diverted_option(self):
        text = r"""
        add 65534 allow ip from any to any diverted keep-state
        """
        parse(text)

    def test_log_logamount(self):
        text = r"""
        add deny log logamount 500 all from any to any
        """
        parse(text)

    def test_named_port(self):
        text = r"""
        add allow udp from { _YANDEXNETS_ } bootpc,bootps to me bootps
        """
        parse(text)

    def test_ipv6(self):
        text = r"""
        add allow tcp from ::/:: to any 80
        add allow tcp from ::1 to any 80
        add allow tcp from ::2:1 to any 80
        add allow tcp from ::3:2:1 to any 80
        add allow tcp from ::4:3:2:1 to any 80
        add allow tcp from ::5:4:3:2:1 to any 80
        add allow tcp from ::6:5:4:3:2:1 to any 80
        add allow tcp from ::7:6:5:4:3:2:1 to any 80
        add allow tcp from 8:7:6:5:4:3:2:1 to any 80
        """
        parse(text)

    def test_table(self):
        text = r"""
        table _ROUTERLOOPBACKS_ add 5.45.193.144/29
        table _ROUTERLOOPBACKS_ add 5.45.200.24/30
        table _ROUTERLOOPBACKS_ add 5.45.203.64/31
        """
        parse(text)

    def test_comment(self):
        text = r"""
        # comment
        """
        parse(text)

    def test_empty_comment(self):
        text = r"""
        #
        """
        parse(text)

    def test_rule_comment(self):
        text = r"""
        add count ip from any to { _MDS_STORAGE_TUN64_ } // TUN64_TO_MDS
        """
        parse(text)

    def test_count(self):
        text = r"""
        add count ip from any to any
        """
        parse(text)

    def test_check_state(self):
        text = r"""
        add check-state
        """
        parse(text)

    def test_tag(self):
        text = r"""
        add allow tag 653 ip4 from { 10.0.0.0/8 } to { _C_RND_DC_ }
        """
        parse(text)

    def test_skipto_tablearg(self):
        text = r"""
        table _SKIPTO_SRC_PREFIX_ add 5.45.192.0/18 :TUN64_TOWORLD_FASTTCP
        table _SKIPTO_SRC_PREFIX_ add 80.239.142.160/27 :TUN64_TOWORLD_TURBO
        table _SKIPTO_SRC_PREFIX_ add 77.88.46.0/25 :TUN64_TOWORLD_MEDIASTORAGE
        table _SKIPTO_DST_PREFIX_ add 213.180.200.0/25 :TUN64_FROMWORLD_MEDIASTORAGE
        table _SKIPTO_DST_PREFIX_ add 141.8.182.48/30 :TUN64_FROMWORLD_FASTTCP_DNS
        table _SKIPTO_DST_PREFIX_ add 149.5.241.0/28 :TUN64_FROMWORLD_FASTTCP_DNS
        add skipto tablearg ip from table(_SKIPTO_SRC_PREFIX_) to any
        add skipto tablearg ip from any to table(_SKIPTO_DST_PREFIX_)
        """
        parse(text)

    def test_allow_from_any(self):
        text = r"""
        ALLOW_FROM_ANY(tcp, { pull-mirror.yandex.net }, 873)
        """
        parse(text)

    def test_allow_from_any_many_ports(self):
        text = r"""
        ALLOW_FROM_ANY(tcp, { pull-mirror.yandex.net }, 873, 123)
        """
        parse(text)

    def test_allow_from_yandexnets(self):
        text = r"""
        ALLOW_FROM_YANDEXNETS(tcp, { pull-mirror.yandex.net }, 873)
        """
        parse(text)
