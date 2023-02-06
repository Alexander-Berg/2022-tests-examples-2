from data.lib import Data


class Data1(Data):
    content = """
Neighbor                             Linklayer Address  Netif Expire    S Flags
fe80::225:90ff:fe34:6acc%vlan811     00:25:90:34:6a:cc vlan811 permanent R
2a02:6b8:0:4401::1                   00:25:90:34:6a:cc vlan401 permanent R
2a02:6b8:0:4401::2                   00:25:90:0e:a5:30 vlan401 7s        R R
fe80::225:90ff:fe34:6acc%vlan401     00:25:90:34:6a:cc vlan401 permanent R
fe80::225:90ff:fe34:6acd%igb1        00:25:90:34:6a:cd   igb1 permanent R
fe80::225:90ff:fe34:6acc%igb0        00:25:90:34:6a:cc   igb0 permanent R
    """
    cmd = "ndp -an"
    host = "vobla"
    version = """
FreeBSD vobla.yndx.net 12.0-E45 FreeBSD 12.0-E45 #0 7f19496ce00(noc12n): Wed Dec 26 16:05:44 UTC 2018     root@noc12-default-job-03:/wrkdirs/usr/ports/local/freebsd12-kernel/work/stage/obj/usr/src/sys/GENERIC  amd64
    """
    result = [{'interface': 'vlan811',
               'ip': 'fe80::225:90ff:fe34:6acc',
               'mac': '00:25:90:34:6a:cc'},
              {'interface': 'vlan401',
               'ip': '2a02:6b8:0:4401::1',
               'mac': '00:25:90:34:6a:cc'},
              {'interface': 'vlan401',
               'ip': '2a02:6b8:0:4401::2',
               'mac': '00:25:90:0e:a5:30'},
              {'interface': 'vlan401',
               'ip': 'fe80::225:90ff:fe34:6acc',
               'mac': '00:25:90:34:6a:cc'},
              {'interface': 'igb1',
               'ip': 'fe80::225:90ff:fe34:6acd',
               'mac': '00:25:90:34:6a:cd'},
              {'interface': 'igb0',
               'ip': 'fe80::225:90ff:fe34:6acc',
               'mac': '00:25:90:34:6a:cc'}]
