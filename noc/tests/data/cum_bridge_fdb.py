from data.lib import Data


class Data1(Data):
    content = """
24:8a:07:f5:0a:18 dev swp1s0 master bridge permanent
c4:54:44:23:c9:b2 dev swp1s0 vlan 742 master bridge
c4:54:44:23:c9:b2 dev swp1s0 vlan 1354 master bridge
24:8a:07:f5:0a:19 dev swp1s1 master bridge permanent
c4:54:44:23:c7:1a dev swp1s1 vlan 867 master bridge
c4:54:44:23:c7:1a dev swp1s1 vlan 788 master bridge
c4:54:44:23:c7:1a dev swp1s1 vlan 688 master bridge
c4:54:44:23:c7:1a dev swp1s1 vlan 549 master bridge
c4:54:44:23:c7:2c dev swp1s2 vlan 867 master bridge
c4:54:44:23:c7:2c dev swp1s2 vlan 688 master bridge
c4:54:44:23:c7:2c dev swp1s2 vlan 549 master bridge
24:8a:07:f5:0a:1a dev swp1s2 master bridge permanent
c4:54:44:23:c7:2c dev swp1s2 vlan 788 master bridge
08:9e:01:d9:43:3e dev swp1s3 vlan 867 master bridge
24:8a:07:f5:0a:1b dev swp1s3 master bridge permanent
08:9e:01:d9:43:3e dev swp1s3 vlan 788 master bridge
08:9e:01:d9:43:3e dev swp1s3 vlan 688 master bridge
08:9e:01:d9:43:3e dev swp1s3 vlan 549 master bridge
c4:54:44:23:c9:68 dev swp2s0 vlan 867 master bridge
c4:54:44:23:c9:68 dev swp2s0 vlan 788 master bridge
c4:54:44:23:c9:68 dev swp2s0 vlan 549 master bridge
c4:54:44:23:c9:68 dev swp2s0 vlan 688 master bridge
24:8a:07:f5:0a:1c dev swp2s0 master bridge permanent
c4:54:44:23:c9:4c dev swp2s1 vlan 688 master bridge
c4:54:44:23:c9:4c dev swp2s1 vlan 549 master bridge
c4:54:44:23:c9:4c dev swp2s1 vlan 867 master bridge
c4:54:44:23:c9:4c dev swp2s1 vlan 788 master bridge
24:8a:07:f5:0a:1d dev swp2s1 master bridge permanent
c4:54:44:23:c8:7e dev swp2s2 vlan 788 master bridge
c4:54:44:23:c8:7e dev swp2s2 vlan 549 master bridge
c4:54:44:23:c8:7e dev swp2s2 vlan 688 master bridge
24:8a:07:f5:0a:1e dev swp2s2 master bridge permanent
c4:54:44:23:c8:7e dev swp2s2 vlan 867 master bridge
c4:54:44:23:c9:70 dev swp2s3 vlan 549 master bridge
c4:54:44:23:c9:70 dev swp2s3 vlan 788 master bridge
c4:54:44:23:c9:70 dev swp2s3 vlan 688 master bridge
24:8a:07:f5:0a:1f dev swp2s3 master bridge permanent
c4:54:44:23:c9:70 dev swp2s3 vlan 867 master bridge
c4:54:44:23:c7:00 dev swp3s0 vlan 867 master bridge
c4:54:44:23:c7:00 dev swp3s0 vlan 688 master bridge
c4:54:44:23:c7:00 dev swp3s0 vlan 549 master bridge
24:8a:07:f5:0a:10 dev swp3s0 master bridge permanent
c4:54:44:23:c7:00 dev swp3s0 vlan 788 master bridge
c4:54:44:23:c7:a4 dev swp3s1 vlan 788 master bridge
c4:54:44:23:c7:a4 dev swp3s1 vlan 867 master bridge
24:8a:07:f5:0a:11 dev swp3s1 master bridge permanent
c4:54:44:23:c7:a4 dev swp3s1 vlan 549 master bridge
c4:54:44:23:c7:a4 dev swp3s1 vlan 688 master bridge
c4:54:44:23:c6:d2 dev swp3s2 vlan 867 master bridge
24:8a:07:f5:0a:12 dev swp3s2 master bridge permanent
c4:54:44:23:c6:d2 dev swp3s2 vlan 688 master bridge
c4:54:44:23:c6:d2 dev swp3s2 vlan 549 master bridge
c4:54:44:23:c6:d2 dev swp3s2 vlan 788 master bridge
24:8a:07:f5:0a:13 dev swp3s3 master bridge permanent
c4:54:44:23:c7:98 dev swp3s3 vlan 867 master bridge
c4:54:44:23:c7:98 dev swp3s3 vlan 788 master bridge
c4:54:44:23:c7:98 dev swp3s3 vlan 549 master bridge
c4:54:44:23:c7:98 dev swp3s3 vlan 688 master bridge
c4:54:44:23:c9:74 dev swp4s0 vlan 549 master bridge
c4:54:44:23:c9:74 dev swp4s0 vlan 788 master bridge
c4:54:44:23:c9:74 dev swp4s0 vlan 867 master bridge
24:8a:07:f5:0a:14 dev swp4s0 master bridge permanent
c4:54:44:23:c9:74 dev swp4s0 vlan 688 master bridge
c4:54:44:23:c9:b0 dev swp4s1 vlan 549 master bridge
c4:54:44:23:c9:b0 dev swp4s1 vlan 688 master bridge
24:8a:07:f5:0a:15 dev swp4s1 master bridge permanent
c4:54:44:23:c9:b0 dev swp4s1 vlan 867 master bridge
c4:54:44:23:c9:b0 dev swp4s1 vlan 788 master bridge
c4:54:44:23:c9:4e dev swp4s2 vlan 549 master bridge
24:8a:07:f5:0a:16 dev swp4s2 master bridge permanent
c4:54:44:23:c9:4e dev swp4s2 vlan 867 master bridge
c4:54:44:23:c9:4e dev swp4s2 vlan 788 master bridge
c4:54:44:23:c9:4e dev swp4s2 vlan 688 master bridge
c4:54:44:23:c9:46 dev swp4s3 vlan 867 master bridge
c4:54:44:23:c9:46 dev swp4s3 vlan 688 master bridge
c4:54:44:23:c9:46 dev swp4s3 vlan 788 master bridge
24:8a:07:f5:0a:17 dev swp4s3 master bridge permanent
c4:54:44:23:c9:46 dev swp4s3 vlan 549 master bridge
24:8a:07:f5:0a:08 dev swp5s0 master bridge permanent
08:9e:01:d9:43:1c dev swp5s0 vlan 688 master bridge
08:9e:01:d9:43:1c dev swp5s0 vlan 788 master bridge
08:9e:01:d9:43:1c dev swp5s0 vlan 867 master bridge
08:9e:01:d9:43:1c dev swp5s0 vlan 549 master bridge
08:9e:01:d9:43:d2 dev swp5s1 vlan 688 master bridge
08:9e:01:d9:43:d2 dev swp5s1 vlan 788 master bridge
24:8a:07:f5:0a:09 dev swp5s1 master bridge permanent
08:9e:01:d9:43:d2 dev swp5s1 vlan 549 master bridge
08:9e:01:d9:43:d2 dev swp5s1 vlan 867 master bridge
c4:54:44:23:c7:28 dev swp5s2 vlan 688 master bridge
c4:54:44:23:c7:28 dev swp5s2 vlan 788 master bridge
c4:54:44:23:c7:28 dev swp5s2 vlan 867 master bridge
24:8a:07:f5:0a:0a dev swp5s2 master bridge permanent
c4:54:44:23:c7:28 dev swp5s2 vlan 549 master bridge
c4:54:44:23:c7:80 dev swp5s3 vlan 867 master bridge
24:8a:07:f5:0a:0b dev swp5s3 master bridge permanent
c4:54:44:23:c7:80 dev swp5s3 vlan 688 master bridge
c4:54:44:23:c7:80 dev swp5s3 vlan 788 master bridge
c4:54:44:23:c7:80 dev swp5s3 vlan 549 master bridge
c4:54:44:23:c6:b8 dev swp6s0 vlan 867 master bridge
24:8a:07:f5:0a:0c dev swp6s0 master bridge permanent
c4:54:44:23:c6:b8 dev swp6s0 vlan 688 master bridge
c4:54:44:23:c6:b8 dev swp6s0 vlan 788 master bridge
c4:54:44:23:c6:b8 dev swp6s0 vlan 549 master bridge
08:9e:01:d9:43:4c dev swp6s1 vlan 549 master bridge
24:8a:07:f5:0a:0d dev swp6s1 master bridge permanent
08:9e:01:d9:43:4c dev swp6s1 vlan 867 master bridge
08:9e:01:d9:43:4c dev swp6s1 vlan 788 master bridge
08:9e:01:d9:43:4c dev swp6s1 vlan 688 master bridge
08:9e:01:d9:43:48 dev swp6s2 vlan 867 master bridge
08:9e:01:d9:43:48 dev swp6s2 vlan 549 master bridge
08:9e:01:d9:43:48 dev swp6s2 vlan 688 master bridge
24:8a:07:f5:0a:0e dev swp6s2 master bridge permanent
08:9e:01:d9:43:48 dev swp6s2 vlan 788 master bridge
24:8a:07:f5:0a:0f dev swp6s3 master bridge permanent
c4:54:44:23:c7:88 dev swp6s3 vlan 688 master bridge
c4:54:44:23:c7:88 dev swp6s3 vlan 867 master bridge
c4:54:44:23:c7:88 dev swp6s3 vlan 788 master bridge
c4:54:44:23:c7:88 dev swp6s3 vlan 549 master bridge
c4:54:44:23:c9:8c dev swp7s0 vlan 688 master bridge
c4:54:44:23:c9:8c dev swp7s0 vlan 788 master bridge
c4:54:44:23:c9:8c dev swp7s0 vlan 549 master bridge
24:8a:07:f5:0a:00 dev swp7s0 master bridge permanent
c4:54:44:23:c9:8c dev swp7s0 vlan 867 master bridge
24:8a:07:f5:0a:01 dev swp7s1 master bridge permanent
c4:54:44:23:c8:d6 dev swp7s1 vlan 867 master bridge
c4:54:44:23:c8:d6 dev swp7s1 vlan 549 master bridge
c4:54:44:23:c8:d6 dev swp7s1 vlan 788 master bridge
c4:54:44:23:c8:d6 dev swp7s1 vlan 688 master bridge
c4:54:44:23:c7:86 dev swp7s2 vlan 788 master bridge
c4:54:44:23:c7:86 dev swp7s2 vlan 867 master bridge
24:8a:07:f5:0a:02 dev swp7s2 master bridge permanent
c4:54:44:23:c7:86 dev swp7s2 vlan 549 master bridge
c4:54:44:23:c7:86 dev swp7s2 vlan 688 master bridge
c4:54:44:23:c9:3a dev swp7s3 vlan 549 master bridge
c4:54:44:23:c9:3a dev swp7s3 vlan 688 master bridge
24:8a:07:f5:0a:03 dev swp7s3 master bridge permanent
c4:54:44:23:c9:3a dev swp7s3 vlan 867 master bridge
c4:54:44:23:c9:3a dev swp7s3 vlan 788 master bridge
24:8a:07:f5:0a:04 dev swp8s0 master bridge permanent
c4:54:44:23:c7:f4 dev swp8s0 vlan 549 master bridge
c4:54:44:23:c7:f4 dev swp8s0 vlan 867 master bridge
c4:54:44:23:c7:f4 dev swp8s0 vlan 788 master bridge
c4:54:44:23:c7:f4 dev swp8s0 vlan 688 master bridge
24:8a:07:f5:0a:05 dev swp8s1 master bridge permanent
c4:54:44:23:c8:7a dev swp8s1 vlan 688 master bridge
c4:54:44:23:c8:7a dev swp8s1 vlan 788 master bridge
c4:54:44:23:c8:7a dev swp8s1 vlan 549 master bridge
c4:54:44:23:c8:7a dev swp8s1 vlan 867 master bridge
c4:54:44:23:c6:dc dev swp8s2 vlan 688 master bridge
c4:54:44:23:c6:dc dev swp8s2 vlan 549 master bridge
c4:54:44:23:c6:dc dev swp8s2 vlan 867 master bridge
24:8a:07:f5:0a:06 dev swp8s2 master bridge permanent
c4:54:44:23:c6:dc dev swp8s2 vlan 788 master bridge
c4:54:44:23:c7:36 dev swp8s3 vlan 549 master bridge
24:8a:07:f5:0a:07 dev swp8s3 master bridge permanent
c4:54:44:23:c7:36 dev swp8s3 vlan 788 master bridge
c4:54:44:23:c7:36 dev swp8s3 vlan 867 master bridge
c4:54:44:23:c7:36 dev swp8s3 vlan 688 master bridge
c4:54:44:23:c7:92 dev swp9s0 vlan 549 master bridge
24:8a:07:f5:0a:24 dev swp9s0 master bridge permanent
c4:54:44:23:c7:92 dev swp9s0 vlan 867 master bridge
c4:54:44:23:c7:92 dev swp9s0 vlan 788 master bridge
c4:54:44:23:c7:92 dev swp9s0 vlan 688 master bridge
24:8a:07:f5:0a:25 dev swp9s1 master bridge permanent
c4:54:44:23:c8:42 dev swp9s1 vlan 688 master bridge
c4:54:44:23:c8:42 dev swp9s1 vlan 788 master bridge
c4:54:44:23:c8:42 dev swp9s1 vlan 549 master bridge
c4:54:44:23:c8:42 dev swp9s1 vlan 867 master bridge
c4:54:44:23:c9:50 dev swp9s2 vlan 688 master bridge
c4:54:44:23:c9:50 dev swp9s2 vlan 788 master bridge
24:8a:07:f5:0a:26 dev swp9s2 master bridge permanent
c4:54:44:23:c9:50 dev swp9s2 vlan 867 master bridge
c4:54:44:23:c9:50 dev swp9s2 vlan 549 master bridge
c4:54:44:23:c9:d4 dev swp9s3 vlan 688 master bridge
c4:54:44:23:c9:d4 dev swp9s3 vlan 549 master bridge
24:8a:07:f5:0a:27 dev swp9s3 master bridge permanent
c4:54:44:23:c9:d4 dev swp9s3 vlan 788 master bridge
c4:54:44:23:c9:d4 dev swp9s3 vlan 867 master bridge
c4:54:44:23:c7:7c dev swp10s0 vlan 688 master bridge
24:8a:07:f5:0a:20 dev swp10s0 master bridge permanent
c4:54:44:23:c7:7c dev swp10s0 vlan 867 master bridge
c4:54:44:23:c7:7c dev swp10s0 vlan 788 master bridge
c4:54:44:23:c7:7c dev swp10s0 vlan 549 master bridge
c4:54:44:23:c7:06 dev swp10s1 vlan 549 master bridge
c4:54:44:23:c7:06 dev swp10s1 vlan 688 master bridge
c4:54:44:23:c7:06 dev swp10s1 vlan 867 master bridge
c4:54:44:23:c7:06 dev swp10s1 vlan 788 master bridge
24:8a:07:f5:0a:21 dev swp10s1 master bridge permanent
c4:54:44:23:c7:3e dev swp10s2 vlan 867 master bridge
24:8a:07:f5:0a:22 dev swp10s2 master bridge permanent
c4:54:44:23:c7:3e dev swp10s2 vlan 549 master bridge
c4:54:44:23:c7:3e dev swp10s2 vlan 788 master bridge
c4:54:44:23:c7:3e dev swp10s2 vlan 688 master bridge
c4:54:44:23:c7:24 dev swp10s3 vlan 549 master bridge
c4:54:44:23:c7:24 dev swp10s3 vlan 688 master bridge
c4:54:44:23:c7:24 dev swp10s3 vlan 867 master bridge
24:8a:07:f5:0a:23 dev swp10s3 master bridge permanent
c4:54:44:23:c7:24 dev swp10s3 vlan 788 master bridge
24:8a:07:f5:0a:2c dev swp11s0 master bridge permanent
24:8a:07:f5:0a:2d dev swp11s1 master bridge permanent
24:8a:07:f5:0a:2e dev swp11s2 master bridge permanent
24:8a:07:f5:0a:2f dev swp11s3 master bridge permanent
24:8a:07:f5:0a:28 dev swp12s0 master bridge permanent
24:8a:07:f5:0a:29 dev swp12s1 master bridge permanent
24:8a:07:f5:0a:2a dev swp12s2 master bridge permanent
24:8a:07:f5:0a:2b dev swp12s3 master bridge permanent
1e:6b:cf:68:96:a8 dev dummy0 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 549 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 333 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 867 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 1354 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 788 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 742 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 688 master bridge permanent
1e:6b:cf:68:96:a8 dev bridge vlan 542 master bridge permanent
    """
    cmd = "/sbin/bridge fdb"
    host = "sas2-5s76"
    version = """
Linux sas2-5s76.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux
    """
    result = [{'interface': 'swp1s0', 'mac': 'c4:54:44:23:c9:b2', 'vlan': '742'},
              {'interface': 'swp1s0', 'mac': 'c4:54:44:23:c9:b2', 'vlan': '1354'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '867'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '788'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '688'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '549'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '867'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '688'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '549'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '788'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '867'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '788'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '688'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '549'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '867'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '788'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '549'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '688'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '688'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '549'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '867'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '788'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '788'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '549'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '688'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '867'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '549'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '788'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '688'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '867'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '867'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '688'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '549'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '788'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '788'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '867'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '549'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '688'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '867'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '688'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '549'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '788'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '867'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '788'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '549'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '688'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '549'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '788'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '867'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '688'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '549'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '688'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '867'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '788'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '549'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '867'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '788'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '688'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '867'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '688'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '788'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '549'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '688'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '788'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '867'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '549'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '688'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '788'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '549'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '867'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '688'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '788'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '867'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '549'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '867'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '688'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '788'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '549'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '867'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '688'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '788'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '549'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '549'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '867'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '788'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '688'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '867'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '549'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '688'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '788'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '688'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '867'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '788'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '549'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '688'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '788'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '549'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '867'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '867'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '549'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '788'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '688'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '788'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '867'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '549'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '688'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '549'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '688'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '867'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '788'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '549'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '867'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '788'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '688'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '688'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '788'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '549'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '867'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '688'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '549'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '867'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '788'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '549'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '788'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '867'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '688'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '549'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '867'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '788'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '688'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '688'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '788'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '549'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '867'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '688'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '788'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '867'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '549'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '688'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '549'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '788'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '867'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '688'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '867'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '788'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '549'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '549'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '688'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '867'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '788'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '867'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '549'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '788'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '688'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '549'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '688'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '867'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '788'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '549'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '333'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '867'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '1354'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '788'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '742'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '688'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '542'}]
