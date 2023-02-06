from data.lib import Data


class Data1(Data):
    content = """
State  Name        Spd   MTU    Mode           LLDP                                       Summary
-----  ----------  ----  -----  -------------  -----------------------------------------  ----------------------------
UP     lo          N/A   65536  Loopback                                                  IP: 127.0.0.1/8
       lo                                                                                 IP: ::1/128
UP     eth0        100M  1500   Mgmt           sas2-i32 (GigabitEthernet0/0/48)           IP: 178.154.176.69/22
UP     swp1s0      10G   9000   Trunk/L2       solomon-kfront-sas-01 (c4:54:44:23:c9:b2)  Master: bridge(UP)
UP     swp1s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp1s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp1s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp2s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp2s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp2s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp2s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp3s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp3s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp3s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp3s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp4s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp4s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp4s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp4s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp5s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp5s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp5s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp5s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp6s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp6s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp6s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp6s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp7s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp7s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp7s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp7s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp8s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp8s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp8s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp8s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp9s0      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp9s1      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp9s2      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp9s3      10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp10s0     10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp10s1     10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp10s2     10G   9000   Trunk/L2                                                  Master: bridge(UP)
UP     swp10s3     10G   9000   Trunk/L2                                                  Master: bridge(UP)
DN     swp11s0     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp11s1     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp11s2     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp11s3     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp12s0     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp12s1     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp12s2     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp12s3     N/A   9000   Access/L2                                                 Master: bridge(UP)
DN     swp13       N/A   9000   NotConfigured
UP     swp14       100G  9000   NotConfigured  sas2-5d2 (100GE6/0/17)
UP     swp14.3001  100G  9000   NotConfigured                                             Master: Nalivka(UP)
UP     swp14.3002  100G  9000   NotConfigured                                             Master: Hbf(UP)
DN     swp15       N/A   9000   NotConfigured
UP     swp16       100G  9000   NotConfigured  sas2-5d4 (100GE6/0/17)
UP     swp16.3001  100G  9000   NotConfigured                                             Master: Nalivka(UP)
UP     swp16.3002  100G  9000   NotConfigured                                             Master: Hbf(UP)
UP     Hbf         N/A   65536  NotConfigured
UP     Nalivka     N/A   65536  NotConfigured
UP     bridge      N/A   9000   Bridge/L2
UP     dummy0      N/A   9000   Access/L2                                                 Master: bridge(UP)
UP     vlan333     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan333                                                                            IP: 10.129.77.1/24
       vlan333                                                                            IP: 2a02:6b8:c02:313::1/64
UP     vlan542     N/A   9000   Interface/L3                                              Master: Nalivka(UP)
       vlan542                                                                            IP: 10.130.30.1/24
       vlan542                                                                            IP: 2a02:6b8:b060:120e::1/64
UP     vlan549     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan549                                                                            IP: 10.130.37.1/24
       vlan549                                                                            IP: 2a02:6b8:b040:1a0f::1/64
UP     vlan688     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan688                                                                            IP: 2a02:6b8:c10:2700::1/57
UP     vlan742     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan742                                                                            IP: 2a02:6b8:f000:910c::1/64
UP     vlan788     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan788                                                                            IP: 2a02:6b8:fc0a:2700::1/57
UP     vlan867     N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan867                                                                            IP: 2a02:6b8:f000:9007::1/64
UP     vlan1354    N/A   9000   Interface/L3                                              Master: Hbf(UP)
       vlan1354                                                                           IP: 2a02:6b8:b000:400::1/64
    """
    cmd = "sudo net show interface all"
    host = "sas2-5s76"
    version = """
Linux sas2-5s76.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux
    """
    result = [{'interface': 'lo', 'state': 'UP'},
              {'interface': 'eth0', 'state': 'UP'},
              {'interface': 'swp1s0', 'state': 'UP'},
              {'interface': 'swp1s1', 'state': 'UP'},
              {'interface': 'swp1s2', 'state': 'UP'},
              {'interface': 'swp1s3', 'state': 'UP'},
              {'interface': 'swp2s0', 'state': 'UP'},
              {'interface': 'swp2s1', 'state': 'UP'},
              {'interface': 'swp2s2', 'state': 'UP'},
              {'interface': 'swp2s3', 'state': 'UP'},
              {'interface': 'swp3s0', 'state': 'UP'},
              {'interface': 'swp3s1', 'state': 'UP'},
              {'interface': 'swp3s2', 'state': 'UP'},
              {'interface': 'swp3s3', 'state': 'UP'},
              {'interface': 'swp4s0', 'state': 'UP'},
              {'interface': 'swp4s1', 'state': 'UP'},
              {'interface': 'swp4s2', 'state': 'UP'},
              {'interface': 'swp4s3', 'state': 'UP'},
              {'interface': 'swp5s0', 'state': 'UP'},
              {'interface': 'swp5s1', 'state': 'UP'},
              {'interface': 'swp5s2', 'state': 'UP'},
              {'interface': 'swp5s3', 'state': 'UP'},
              {'interface': 'swp6s0', 'state': 'UP'},
              {'interface': 'swp6s1', 'state': 'UP'},
              {'interface': 'swp6s2', 'state': 'UP'},
              {'interface': 'swp6s3', 'state': 'UP'},
              {'interface': 'swp7s0', 'state': 'UP'},
              {'interface': 'swp7s1', 'state': 'UP'},
              {'interface': 'swp7s2', 'state': 'UP'},
              {'interface': 'swp7s3', 'state': 'UP'},
              {'interface': 'swp8s0', 'state': 'UP'},
              {'interface': 'swp8s1', 'state': 'UP'},
              {'interface': 'swp8s2', 'state': 'UP'},
              {'interface': 'swp8s3', 'state': 'UP'},
              {'interface': 'swp9s0', 'state': 'UP'},
              {'interface': 'swp9s1', 'state': 'UP'},
              {'interface': 'swp9s2', 'state': 'UP'},
              {'interface': 'swp9s3', 'state': 'UP'},
              {'interface': 'swp10s0', 'state': 'UP'},
              {'interface': 'swp10s1', 'state': 'UP'},
              {'interface': 'swp10s2', 'state': 'UP'},
              {'interface': 'swp10s3', 'state': 'UP'},
              {'interface': 'swp11s0', 'state': 'DN'},
              {'interface': 'swp11s1', 'state': 'DN'},
              {'interface': 'swp11s2', 'state': 'DN'},
              {'interface': 'swp11s3', 'state': 'DN'},
              {'interface': 'swp12s0', 'state': 'DN'},
              {'interface': 'swp12s1', 'state': 'DN'},
              {'interface': 'swp12s2', 'state': 'DN'},
              {'interface': 'swp12s3', 'state': 'DN'},
              {'interface': 'swp13', 'state': 'DN'},
              {'interface': 'swp14', 'state': 'UP'},
              {'interface': 'swp14.3001', 'state': 'UP'},
              {'interface': 'swp14.3002', 'state': 'UP'},
              {'interface': 'swp15', 'state': 'DN'},
              {'interface': 'swp16', 'state': 'UP'},
              {'interface': 'swp16.3001', 'state': 'UP'},
              {'interface': 'swp16.3002', 'state': 'UP'},
              {'interface': 'Hbf', 'state': 'UP'},
              {'interface': 'Nalivka', 'state': 'UP'},
              {'interface': 'bridge', 'state': 'UP'},
              {'interface': 'dummy0', 'state': 'UP'},
              {'interface': 'vlan333', 'state': 'UP'},
              {'interface': 'vlan542', 'state': 'UP'},
              {'interface': 'vlan549', 'state': 'UP'},
              {'interface': 'vlan688', 'state': 'UP'},
              {'interface': 'vlan742', 'state': 'UP'},
              {'interface': 'vlan788', 'state': 'UP'},
              {'interface': 'vlan867', 'state': 'UP'},
              {'interface': 'vlan1354', 'state': 'UP'}]
