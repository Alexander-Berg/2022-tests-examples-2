from unittest import mock

import snmpd_lib
import snmpd_sysfs

OID_BASE = ".1.3.6.1.4.1.11069.320.531"


class MockOsWalk:
    def __init__(self, data):
        self.data = data

    def __call__(self, path):
        if path in self.data:
            return self.data[path]
        return []


class MockOpen:
    def __init__(self, data):
        self.data = data

    def __call__(self, file, mode='r', buffering=None, encoding=None, errors=None, newline=None, closefd=True):
        if file in self.data:
            return MockOpenFile(self.data[file])
        raise Exception("unknown file %s" % file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def read(self):
        return


class MockOpenFile:
    def __init__(self, res):
        self.res = res

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def read(self):
        return self.res


@mock.patch("snmpd_sysfs.os.walk")
@mock.patch("snmpd_sysfs.open")
def test_pass_persist(open_mock, os_walk_mock):
    os_walk_mock.side_effect = MockOsWalk(
        {"/sys/class/net/": [("/sys/class/net/", ["swp8s1", "swp24s0", "swp12s0"], ["bonding_masters"])]}
    )
    open_mock.side_effect = MockOpen(
        {
            "/sys/class/net/swp8s1/ifindex": "81\n",
            "/sys/class/net/swp24s0/ifindex": "240\n",
            "/sys/class/net/swp12s0/ifindex": "120\n",
            "/sys/class/net/swp8s1/carrier_changes": "0\n",
            "/sys/class/net/swp24s0/carrier_changes": "10\n",
            "/sys/class/net/swp12s0/carrier_changes": "20\n",
        }
    )
    pp = snmpd_lib.PassPersist(OID_BASE)
    ss = snmpd_sysfs.SnmpdPass(pp)
    ss.update()
    assert ss.ports == [('120', 'swp12s0'), ('240', 'swp24s0'), ('81', 'swp8s1')]
    assert ss.last_port_data == [
        ('120', 'swp12s0', {'carrier_changes': '20'}),
        ('240', 'swp24s0', {'carrier_changes': '10'}),
        ('81', 'swp8s1', {'carrier_changes': '0'}),
    ]
    assert pp.pending == {
        '2.1': {'type': 'STRING', 'value': 'ifname'},
        '2.2': {'type': 'STRING', 'value': 'sysfs counter name'},
        '2.3': {'type': 'STRING', 'value': 'carrier_changes'},
        '1.120': {'type': 'STRING', 'value': 'swp12s0'},
        '1.240': {'type': 'STRING', 'value': 'swp24s0'},
        '1.81': {'type': 'STRING', 'value': 'swp8s1'},
        '3.120': {'type': 'Counter64', 'value': '20'},
        '3.240': {'type': 'Counter64', 'value': '10'},
        '3.81': {'type': 'Counter64', 'value': '0'},
    }
