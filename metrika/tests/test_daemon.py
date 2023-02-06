import logging
from unittest.mock import Mock

import metrika.admin.python.zooface.recursive_deleter.lib.daemon as daemon
import metrika.pylib.structures.dotdict as dotdict
import metrika.admin.python.zooface.recursive_deleter.lib as lib


class ZoofaceRecursiveDeleterMock(daemon.ZoofaceRecursiveDeleter):
    def run(self):
        self.shutdown.set()
        super().run()
        self.result = 1337

    def get_config(self):
        return dotdict.DotDict.from_dict({'sleep_time': 5, 'workers': 5})

    def init_loggers(self):
        self.logger = logging.getLogger(self.name)

    def start_daemon_services(self):
        return


def test_daemon_stop(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(lib.DeleteHelper, 'process_tasks', lambda self: None)
        m.setattr(lib.DeleteHelper, 'zk_client', Mock())
        deleter = ZoofaceRecursiveDeleterMock('zooface-recursive-deleter')
        deleter.start()
        for slave in deleter.slaves:
            assert not slave.is_alive(), slave
        assert deleter.result == 1337
