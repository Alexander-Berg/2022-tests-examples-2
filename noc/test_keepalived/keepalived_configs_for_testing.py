VALID_KEEPALIVED_CONFIGS = [
    (
        "testenv-ezhichek-service.yandex.net/sas-1testenv-test-lb0aa/2a02:6b8:0:3400:0:4a8:0:ffff-53-TCP.conf",
        """\
# SVC: (1) [dostavkatraffika] testenv-ezhichek-service.yandex.net
# LB: (117) [sas-1testenv-test-lb0aa] sas-1testenv-test-lb0aa.yndx.net
# VS: (181) TCP:2a02:6b8:0:3400:0:4a8:0:ffff

virtual_server 2a02:6b8:0:3400:0:4a8:0:ffff 53 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        real_server 2a02:6b8:b010:31::233 53 {
                # RS: (4) [mnt-sas.yandex.net] 2a02:6b8:b010:31::233
                # RS state ID: 289
                weight 10
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1002
                        retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:0:1482::115 53 {
                # RS: (10) [mnt-myt.yandex.net] 2a02:6b8:0:1482::115
                # RS state ID: 288
                weight 1
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1001
                        retry 1
                        delay_before_retry 1
                }
        }
}""",
    ),
    (
        "testenv-ezhichek-service.yandex.net/sas-1testenv-test-lb0aa/2a02:6b8:0:3400:0:4a8:0:ffff-53-UDP.conf",
        """\
# SVC: (1) [dostavkatraffika] testenv-ezhichek-service.yandex.net
# LB: (117) [sas-1testenv-test-lb0aa] sas-1testenv-test-lb0aa.yndx.net
# VS: (180) UDP:2a02:6b8:0:3400:0:4a8:0:ffff

virtual_server 2a02:6b8:0:3400:0:4a8:0:ffff 53 {
        protocol UDP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        real_server 2a02:6b8:b010:31::233 53 {
                # RS: (4) [mnt-sas.yandex.net] 2a02:6b8:b010:31::233
                # RS state ID: 289
                weight 10
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1002
                        retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:0:1482::115 53 {
                # RS: (10) [mnt-myt.yandex.net] 2a02:6b8:0:1482::115
                # RS state ID: 288
                weight 1
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1001
                        retry 1
                        delay_before_retry 1
                }
        }
}""",
    ),
    (
        "testenv-ezhichek-service.yandex.net/sas-1testenv-test-lb0aa/2a02:6b8:0:3400:0:4a8:0:ffff-443-TCP.conf",
        """\
# SVC: (1) [dostavkatraffika] testenv-ezhichek-service.yandex.net
# LB: (117) [sas-1testenv-test-lb0aa] sas-1testenv-test-lb0aa.yndx.net
# VS: (179) TCP:2a02:6b8:0:3400:0:4a8:0:ffff

virtual_server 2a02:6b8:0:3400:0:4a8:0:ffff 443 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (4) [mnt-sas.yandex.net] 2a02:6b8:b010:31::233
                # RS state ID: 289
                weight 10
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1002
                        retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (10) [mnt-myt.yandex.net] 2a02:6b8:0:1482::115
                # RS state ID: 288
                weight 1
                TCP_CHECK {
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1001
                        retry 1
                        delay_before_retry 1
                }
        }
}""",
    ),
    (
        "testenv-ezhichek-service.yandex.net/sas-1testenv-test-lb0aa/2a02:6b8:0:3400:0:4a8:0:ffff-80-TCP.conf",
        """
# SVC: (1) [dostavkatraffika] testenv-ezhichek-service.yandex.net
# LB: (117) [sas-1testenv-test-lb0aa] sas-1testenv-test-lb0aa.yndx.net
# VS: (178) TCP:2a02:6b8:0:3400:0:4a8:0:ffff

virtual_server 2a02:6b8:0:3400:0:4a8:0:ffff 80 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        real_server 2a02:6b8:b010:31::233 80 {
                # RS: (4) [mnt-sas.yandex.net] 2a02:6b8:b010:31::233
                # RS state ID: 289
                weight 10
                HTTP_GET {
                        url {
                                path /ping
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1002
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:0:1482::115 80 {
                # RS: (10) [mnt-myt.yandex.net] 2a02:6b8:0:1482::115
                # RS state ID: 288
                weight 1
                HTTP_GET {
                        url {
                                path /ping
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400:0:4a8:0:ffff
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1001
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}""",
    ),
]

VALID_KEEPALIVED_CONFIG: str = "".join(f"# {path}\n{config}\n" for path, config in VALID_KEEPALIVED_CONFIGS)

EMPTY_KEEPALIVED_CONFIG: str = ""
