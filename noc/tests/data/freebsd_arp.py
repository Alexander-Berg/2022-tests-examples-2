from data.lib import Data


class Data1(Data):
    content = """
? (213.221.40.129) at 10:f3:11:3a:0e:c9 on vlan811 expires in 1199 seconds [vlan]
? (213.221.40.130) at 00:25:90:3e:0f:b8 on vlan811 expires in 1133 seconds [vlan]
? (213.221.40.132) at 00:25:90:34:6a:cc on vlan811 permanent [vlan]
? (77.88.60.17) at 00:25:90:34:6a:cc on vlan401 permanent [vlan]
? (77.88.60.19) at (incomplete) on vlan401 expired [vlan]
? (77.88.60.18) at 00:25:90:0e:a5:30 on vlan401 expires in 814 seconds [vlan]
? (77.88.60.21) at (incomplete) on vlan401 expired [vlan]
? (77.88.60.22) at (incomplete) on vlan401 expired [vlan]
? (188.170.183.177) at 4c:1f:cc:a0:ee:23 on igb1 expires in 1197 seconds [ethernet]
? (188.170.183.178) at 00:25:90:34:6a:cd on igb1 permanent [ethernet]
    """
    cmd = "arp -an"
    host = "vobla"
    version = """
FreeBSD vobla.yndx.net 12.0-E45 FreeBSD 12.0-E45 #0 7f19496ce00(noc12n): Wed Dec 26 16:05:44 UTC 2018     root@noc12-default-job-03:/wrkdirs/usr/ports/local/freebsd12-kernel/work/stage/obj/usr/src/sys/GENERIC  amd64
    """
    result = [{'interface': 'vlan811', 'ip': '213.221.40.129', 'mac': '10:f3:11:3a:0e:c9'},
              {'interface': 'vlan811', 'ip': '213.221.40.130', 'mac': '00:25:90:3e:0f:b8'},
              {'interface': 'vlan811', 'ip': '213.221.40.132', 'mac': '00:25:90:34:6a:cc'},
              {'interface': 'vlan401', 'ip': '77.88.60.17', 'mac': '00:25:90:34:6a:cc'},
              {'interface': 'vlan401', 'ip': '77.88.60.18', 'mac': '00:25:90:0e:a5:30'},
              {'interface': 'igb1', 'ip': '188.170.183.177', 'mac': '4c:1f:cc:a0:ee:23'},
              {'interface': 'igb1', 'ip': '188.170.183.178', 'mac': '00:25:90:34:6a:cd'}]
