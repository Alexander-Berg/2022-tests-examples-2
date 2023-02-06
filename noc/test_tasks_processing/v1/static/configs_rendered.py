TASK_L4_CONFIG = """# 2a02:6b8:0:3400::50-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 80 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 2
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 80 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1767
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 80 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1768
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::50-443-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 443 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 5
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
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
                        connect_ip 2a02:6b8:0:3400::50
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


TASK_FWMARK_CONFIG = """# 10-52407.conf
# SVC: mirror.yandex.ru
# VS: (123456) TCP:2a02:6b8::183

virtual_server fwmark 52407 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        ip_family inet6
        delay_loop 5
        virtualhost l3.tt.yandex-team.ru
        persistence_timeout 300
        real_server 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0 {
                # RS: (11554) 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0
                weight 1
                HTTP_GET {
                        url {
                                path /.ok.txt
                                status_code 200
                        }
                        connect_ip 2a02:6b8::183
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2965
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2-52407.conf
# SVC: mirror.yandex.ru
# VS: (123456) TCP:213.180.204.183

virtual_server fwmark 52407 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        ip_family inet
        delay_loop 5
        persistence_timeout 300
        real_server 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0 {
                # RS: (21554) 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0
                weight 1
                HTTP_GET {
                        url {
                                path /.ok.txt
                                status_code 200
                        }
                        connect_ip 213.180.204.183
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2965
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
"""

TASK_DYNAMIC_WEIGHT_CONFIG = """# 2a02:6b8:0:3400::3:16-443-TCP.conf
# SVC: passport-test.yandex.ru
# VS: (2520354) TCP:2a02:6b8:0:3400::3:16

virtual_server 2a02:6b8:0:3400::3:16 443 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 5
        virtualhost passport-test.yandex.ru
        real_server 2a02:6b8:c01:710:8000:611:0:11 443 {
                # RS: (3082264) 2a02:6b8:c01:710:8000:611:0:11
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1564
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
        real_server 2a02:6b8:c03:763:8000:611:0:17 443 {
                # RS: (3082265) 2a02:6b8:c03:763:8000:611:0:17
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2605
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
        real_server 2a02:6b8:c02:500:8000:611:0:d 443 {
                # RS: (3082266) 2a02:6b8:c02:500:8000:611:0:d
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2415
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
}
"""


TASK_L4_CONFIG_ANNOUNCE_ENABLED = """# 2a02:6b8:0:3400::50-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 80 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::50,80/TCP,b-100,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::50,80/TCP,b-100,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 2
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 80 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1767
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 80 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1768
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::50-443-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 443 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::50,443/TCP,b-100,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::50,443/TCP,b-100,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 5
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
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
                        connect_ip 2a02:6b8:0:3400::50
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

TASK_FWMARK_CONFIG_ANNOUNCE_ENABLED = """# 10-52407.conf
# SVC: mirror.yandex.ru
# VS: (123456) TCP:2a02:6b8::183

virtual_server fwmark 52407 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up  2a02:6b8::183,b-100,1"
        quorum_down "/etc/keepalived/quorum-handler2.sh down  2a02:6b8::183,b-100,1"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        ip_family inet6
        delay_loop 5
        virtualhost l3.tt.yandex-team.ru
        persistence_timeout 300
        real_server 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0 {
                # RS: (11554) 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0
                weight 1
                HTTP_GET {
                        url {
                                path /.ok.txt
                                status_code 200
                        }
                        connect_ip 2a02:6b8::183
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2965
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2-52407.conf
# SVC: mirror.yandex.ru
# VS: (123456) TCP:213.180.204.183

virtual_server fwmark 52407 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up  213.180.204.183,b-100,1"
        quorum_down "/etc/keepalived/quorum-handler2.sh down  213.180.204.183,b-100,1"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        ip_family inet
        delay_loop 5
        persistence_timeout 300
        real_server 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0 {
                # RS: (21554) 2a02:6b8:c02:7f4:0:1429:f3fd:d8d0
                weight 1
                HTTP_GET {
                        url {
                                path /.ok.txt
                                status_code 200
                        }
                        connect_ip 213.180.204.183
                        connect_port 80
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2965
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
"""

TASK_DYNAMIC_WEIGHT_CONFIG_ANNOUNCE_ENABLED = """# 2a02:6b8:0:3400::3:16-443-TCP.conf
# SVC: passport-test.yandex.ru
# VS: (2520354) TCP:2a02:6b8:0:3400::3:16

virtual_server 2a02:6b8:0:3400::3:16 443 {
        protocol TCP
        quorum_up   "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::3:16,443/TCP,b-100,2"
        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:0:3400::3:16,443/TCP,b-100,2"
        quorum 1
        hysteresis 0
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 5
        virtualhost passport-test.yandex.ru
        real_server 2a02:6b8:c01:710:8000:611:0:11 443 {
                # RS: (3082264) 2a02:6b8:c01:710:8000:611:0:11
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1564
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
        real_server 2a02:6b8:c03:763:8000:611:0:17 443 {
                # RS: (3082265) 2a02:6b8:c03:763:8000:611:0:17
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2605
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
        real_server 2a02:6b8:c02:500:8000:611:0:d 443 {
                # RS: (3082266) 2a02:6b8:c02:500:8000:611:0:d
                weight 0
                SSL_GET {
                        url {
                                path /ping.html
                                digest 69e24a7fd90ef6988e07480b522d6f80
                                status_code 200
                        }
                        connect_ip 2a02:6b8:0:3400::3:16
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 2415
                        nb_get_retry 1
                        delay_before_retry 1
                        dynamic_weight_enable
                        dynamic_weight_in_header
                        dynamic_weight_coefficient 10000
                }
        }
}
"""

TASK_MAGLEV_AND_HTTP_PROTOCOL_CONFIG = """# 2a02:6b8:0:3400::50-80-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069929) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 80 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched mh
        mh_port
        delay_loop 5
        virtualhost l3.tt.yandex-team.ru
        real_server 2a02:6b8:0:1482::115 80 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1767
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
        real_server 2a02:6b8:b010:31::233 80 {
                # RS: (1555) 2a02:6b8:b010:31::233
                weight 1
                SSL_GET {
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
                        connect_port 443
                        bindto 2a02:6b8:0:e00::13:b0aa
                        connect_timeout 1
                        fwmark 1768
                        nb_get_retry 1
                        delay_before_retry 1
                }
        }
}
# 2a02:6b8:0:3400::50-443-TCP.conf
# SVC: l3.tt.yandex-team.ru
# VS: (1069928) TCP:2a02:6b8:0:3400::50

virtual_server 2a02:6b8:0:3400::50 443 {
        protocol TCP
                # port announce disabled
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        delay_loop 5
        real_server 2a02:6b8:0:1482::115 443 {
                # RS: (1554) 2a02:6b8:0:1482::115
                weight 1
                SSL_GET {
                        http_protocol 1.0C
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
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
                        http_protocol 1.0C
                        url {
                                path /ping
                                status_code 204
                        }
                        connect_ip 2a02:6b8:0:3400::50
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
