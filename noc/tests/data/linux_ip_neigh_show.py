from data.lib import Data


class Data1(Data):
    content = """
213.248.97.4 dev eth1.1692  FAILED
5.255.216.30 dev eth1 lladdr 30:d1:7e:75:71:66 REACHABLE
80.239.201.246 dev eth1.1691 lladdr 30:d1:7e:75:71:6d STALE
149.5.241.238 dev eth1.1692 lladdr 30:d1:7e:75:71:6e STALE
74.125.131.139 dev eth1.1691  FAILED
213.248.97.4 dev eth1.1691  FAILED
80.239.201.253 dev eth1.1691  FAILED
74.125.131.102 dev eth1.1691  FAILED
74.125.131.113 dev eth1.1692  FAILED
fe80::1 dev eth1.1691 lladdr 30:d1:7e:75:71:6d router STALE
fe80::1 dev eth1.1699 lladdr 30:d1:7e:75:71:67 router REACHABLE
2a02:6b8:0:efa::1 dev eth1 lladdr 30:d1:7e:75:71:66 router REACHABLE
fe80::1 dev eth1.1692 lladdr 30:d1:7e:75:71:6e router STALE
fe80::1 dev eth1 lladdr 30:d1:7e:75:71:66 router STALE
    """
    cmd = "ip neigh show"
    host = "man1-4lb5a"
    version = """
Linux man1-4lb5a.yndx.net 4.4.102-noc #2 SMP Thu Feb 1 13:33:47 MSK 2018 x86_64 x86_64 x86_64 GNU/Linux
    """
    result = [{'interface': 'eth1', 'ip': '5.255.216.30', 'mac': '30:d1:7e:75:71:66'},
              {'interface': 'eth1.1691', 'ip': '80.239.201.246', 'mac': '30:d1:7e:75:71:6d'},
              {'interface': 'eth1.1692', 'ip': '149.5.241.238', 'mac': '30:d1:7e:75:71:6e'},
              {'interface': 'eth1.1691', 'ip': 'fe80::1', 'mac': '30:d1:7e:75:71:6d'},
              {'interface': 'eth1.1699', 'ip': 'fe80::1', 'mac': '30:d1:7e:75:71:67'},
              {'interface': 'eth1', 'ip': '2a02:6b8:0:efa::1', 'mac': '30:d1:7e:75:71:66'},
              {'interface': 'eth1.1692', 'ip': 'fe80::1', 'mac': '30:d1:7e:75:71:6e'},
              {'interface': 'eth1', 'ip': 'fe80::1', 'mac': '30:d1:7e:75:71:66'}]
