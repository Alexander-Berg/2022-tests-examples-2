from data.lib import Data


class Data1(Data):
    content = r"""
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:a1:ab:98 brd ff:ff:ff:ff:ff:ff
3: swp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:18 brd ff:ff:ff:ff:ff:ff
4: swp1s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:19 brd ff:ff:ff:ff:ff:ff
5: swp1s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1a brd ff:ff:ff:ff:ff:ff
6: swp1s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1b brd ff:ff:ff:ff:ff:ff
7: swp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1c brd ff:ff:ff:ff:ff:ff
8: swp2s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1d brd ff:ff:ff:ff:ff:ff
9: swp2s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1e brd ff:ff:ff:ff:ff:ff
10: swp2s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:1f brd ff:ff:ff:ff:ff:ff
11: swp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:10 brd ff:ff:ff:ff:ff:ff
12: swp3s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:11 brd ff:ff:ff:ff:ff:ff
13: swp3s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:12 brd ff:ff:ff:ff:ff:ff
14: swp3s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:13 brd ff:ff:ff:ff:ff:ff
15: swp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:14 brd ff:ff:ff:ff:ff:ff
16: swp4s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:15 brd ff:ff:ff:ff:ff:ff
17: swp4s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:16 brd ff:ff:ff:ff:ff:ff
18: swp4s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:17 brd ff:ff:ff:ff:ff:ff
19: swp5s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:08 brd ff:ff:ff:ff:ff:ff
20: swp5s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:09 brd ff:ff:ff:ff:ff:ff
21: swp5s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0a brd ff:ff:ff:ff:ff:ff
22: swp5s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0b brd ff:ff:ff:ff:ff:ff
23: swp6s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0c brd ff:ff:ff:ff:ff:ff
24: swp6s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0d brd ff:ff:ff:ff:ff:ff
25: swp6s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0e brd ff:ff:ff:ff:ff:ff
26: swp6s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:0f brd ff:ff:ff:ff:ff:ff
27: swp7s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:00 brd ff:ff:ff:ff:ff:ff
28: swp7s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:01 brd ff:ff:ff:ff:ff:ff
29: swp7s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:02 brd ff:ff:ff:ff:ff:ff
30: swp7s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:03 brd ff:ff:ff:ff:ff:ff
31: swp8s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:04 brd ff:ff:ff:ff:ff:ff
32: swp8s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:05 brd ff:ff:ff:ff:ff:ff
33: swp8s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:06 brd ff:ff:ff:ff:ff:ff
34: swp8s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:07 brd ff:ff:ff:ff:ff:ff
35: swp9s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:24 brd ff:ff:ff:ff:ff:ff
36: swp9s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:25 brd ff:ff:ff:ff:ff:ff
37: swp9s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:26 brd ff:ff:ff:ff:ff:ff
38: swp9s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:27 brd ff:ff:ff:ff:ff:ff
39: swp10s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:20 brd ff:ff:ff:ff:ff:ff
40: swp10s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:21 brd ff:ff:ff:ff:ff:ff
41: swp10s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:22 brd ff:ff:ff:ff:ff:ff
42: swp10s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast master bridge state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:23 brd ff:ff:ff:ff:ff:ff
43: swp11s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2c brd ff:ff:ff:ff:ff:ff
44: swp11s1: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2d brd ff:ff:ff:ff:ff:ff
45: swp11s2: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2e brd ff:ff:ff:ff:ff:ff
46: swp11s3: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2f brd ff:ff:ff:ff:ff:ff
47: swp12s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:28 brd ff:ff:ff:ff:ff:ff
48: swp12s1: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:29 brd ff:ff:ff:ff:ff:ff
49: swp12s2: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2a brd ff:ff:ff:ff:ff:ff
50: swp12s3: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast master bridge state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:2b brd ff:ff:ff:ff:ff:ff
51: swp13: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:34 brd ff:ff:ff:ff:ff:ff
52: swp14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:30 brd ff:ff:ff:ff:ff:ff
53: swp15: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9000 qdisc pfifo_fast state DOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:3c brd ff:ff:ff:ff:ff:ff
54: swp16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:38 brd ff:ff:ff:ff:ff:ff
55: swid0_eth: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9216 qdisc pfifo_fast state UNKNOWN mode DEFAULT group default qlen 1000\    link/ether 24:8a:07:f5:0a:00 brd ff:ff:ff:ff:ff:ff
56: swp14.3002@swp14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 24:8a:07:f5:0a:30 brd ff:ff:ff:ff:ff:ff
57: Hbf: <NOARP,MASTER,UP,LOWER_UP> mtu 65536 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\    link/ether 5e:8b:af:0c:0f:d4 brd ff:ff:ff:ff:ff:ff
58: swp16.3002@swp16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 24:8a:07:f5:0a:38 brd ff:ff:ff:ff:ff:ff
59: dummy0: <BROADCAST,NOARP,UP,LOWER_UP> mtu 9000 qdisc noqueue master bridge state UNKNOWN mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
60: bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
61: vlan333@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
62: vlan549@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
63: vlan688@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
64: vlan742@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
65: vlan788@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
66: vlan867@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
67: vlan1354@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Hbf state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
68: swp14.3001@swp14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Nalivka state UP mode DEFAULT group default \    link/ether 24:8a:07:f5:0a:30 brd ff:ff:ff:ff:ff:ff
69: Nalivka: <NOARP,MASTER,UP,LOWER_UP> mtu 65536 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\    link/ether 4a:46:70:e5:b9:a7 brd ff:ff:ff:ff:ff:ff
70: swp16.3001@swp16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Nalivka state UP mode DEFAULT group default \    link/ether 24:8a:07:f5:0a:38 brd ff:ff:ff:ff:ff:ff
71: vlan542@bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc noqueue master Nalivka state UP mode DEFAULT group default \    link/ether 1e:6b:cf:68:96:a8 brd ff:ff:ff:ff:ff:ff
    """
    cmd = "ip -o link | grep ether"
    host = "sas2-5s76"
    version = """
Linux sas2-5s76.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux
    """
    result = [{'interface': 'eth0', 'state': 'up'},
              {'interface': 'swp1s0', 'state': 'up'},
              {'interface': 'swp1s1', 'state': 'up'},
              {'interface': 'swp1s2', 'state': 'up'},
              {'interface': 'swp1s3', 'state': 'up'},
              {'interface': 'swp2s0', 'state': 'up'},
              {'interface': 'swp2s1', 'state': 'up'},
              {'interface': 'swp2s2', 'state': 'up'},
              {'interface': 'swp2s3', 'state': 'up'},
              {'interface': 'swp3s0', 'state': 'up'},
              {'interface': 'swp3s1', 'state': 'up'},
              {'interface': 'swp3s2', 'state': 'up'},
              {'interface': 'swp3s3', 'state': 'up'},
              {'interface': 'swp4s0', 'state': 'up'},
              {'interface': 'swp4s1', 'state': 'up'},
              {'interface': 'swp4s2', 'state': 'up'},
              {'interface': 'swp4s3', 'state': 'up'},
              {'interface': 'swp5s0', 'state': 'up'},
              {'interface': 'swp5s1', 'state': 'up'},
              {'interface': 'swp5s2', 'state': 'up'},
              {'interface': 'swp5s3', 'state': 'up'},
              {'interface': 'swp6s0', 'state': 'up'},
              {'interface': 'swp6s1', 'state': 'up'},
              {'interface': 'swp6s2', 'state': 'up'},
              {'interface': 'swp6s3', 'state': 'up'},
              {'interface': 'swp7s0', 'state': 'up'},
              {'interface': 'swp7s1', 'state': 'up'},
              {'interface': 'swp7s2', 'state': 'up'},
              {'interface': 'swp7s3', 'state': 'up'},
              {'interface': 'swp8s0', 'state': 'up'},
              {'interface': 'swp8s1', 'state': 'up'},
              {'interface': 'swp8s2', 'state': 'up'},
              {'interface': 'swp8s3', 'state': 'up'},
              {'interface': 'swp9s0', 'state': 'up'},
              {'interface': 'swp9s1', 'state': 'up'},
              {'interface': 'swp9s2', 'state': 'up'},
              {'interface': 'swp9s3', 'state': 'up'},
              {'interface': 'swp10s0', 'state': 'up'},
              {'interface': 'swp10s1', 'state': 'up'},
              {'interface': 'swp10s2', 'state': 'up'},
              {'interface': 'swp10s3', 'state': 'up'},
              {'interface': 'swp11s0', 'state': 'down'},
              {'interface': 'swp11s1', 'state': 'down'},
              {'interface': 'swp11s2', 'state': 'down'},
              {'interface': 'swp11s3', 'state': 'down'},
              {'interface': 'swp12s0', 'state': 'down'},
              {'interface': 'swp12s1', 'state': 'down'},
              {'interface': 'swp12s2', 'state': 'down'},
              {'interface': 'swp12s3', 'state': 'down'},
              {'interface': 'swp13', 'state': 'down'},
              {'interface': 'swp14', 'state': 'up'},
              {'interface': 'swp15', 'state': 'down'},
              {'interface': 'swp16', 'state': 'up'},
              {'interface': 'swid0_eth', 'state': 'up'},
              {'interface': 'Hbf', 'state': 'up'},
              {'interface': 'dummy0', 'state': 'up'},
              {'interface': 'bridge', 'state': 'up'},
              {'interface': 'Nalivka', 'state': 'up'}]
