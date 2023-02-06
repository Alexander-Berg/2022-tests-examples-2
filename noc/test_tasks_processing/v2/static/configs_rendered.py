CONFIG_L4_V2 = """# 2a02:6b8:0:3400::1-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::1-801-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069930) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 801 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::0-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::0

virtual_server 2a02:6b8:0:3400::0 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
"""


CONFIG_L4_ANNOUNCE_DISABLED_V2 = """# 2a02:6b8:0:3400::1-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 80 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::1-801-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069930) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 801 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::0-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::0

virtual_server 2a02:6b8:0:3400::0 80 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
"""


CONFIG_MAGLEV_AND_HTTP_PROTOCOL_V2 = """# 2a02:6b8:0:3400::1-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched mh
        mh_port
        ops
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::1-801-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069930) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 801 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched mh
        mh_port
        ops
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::0-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::0

virtual_server 2a02:6b8:0:3400::0 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched mh
        mh_port
        ops
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
"""


CONFIG_DYNAMIC_WEIGHT_V2 = """# 2a02:6b8:0:3400::1-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,80/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
}
# 2a02:6b8:0:3400::1-801-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069930) TCP:2a02:6b8:0:3400::1

virtual_server 2a02:6b8:0:3400::1 801 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::1,801/TCP,b-300,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::1
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
}
# 2a02:6b8:0:3400::0-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::0

virtual_server 2a02:6b8:0:3400::0 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::0,80/TCP,b-300,1"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 10
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1650
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
        real_server 2a02:6b8:b010:31::233 443 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::0
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1651
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 30
                }
        }
}
"""
