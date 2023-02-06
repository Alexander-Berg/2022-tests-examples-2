import unittest
import unittest.mock
import logging
import socket

from hbf.locks import NO_FORK_LOCK
import hbf.code as hbf

from hbf.lib import show_profileit_results
from hbf.ipaddress2 import ip_network
from hbf.drills import DrillsConfig


class BaseTest(unittest.TestCase):
    HOSTS = {}
    MACROSES = {}
    PROJECTS = {}
    SECTIONS = {}
    DRILLS_CONF = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patches = {}

    def _getaddrinfo(self, hostname, *args, **kwargs):
        if hostname in self.HOSTS:
            ret = self.HOSTS[hostname]
        else:
            raise socket.gaierror(1, "[Errno -2] Name or service not known")
        return [(None, None, None, None, [x]) for x in ret]

    def _macro_iter(self):
        for mname, items in self.MACROSES.items():
            yield mname, tuple([hbf.is_ip_or_net(x) and ip_network(x) or x for x in items])

    def _projects_iter(self):
        for pid, (name, inet) in self.PROJECTS.items():
            pid = hbf.ProjId(int(pid), str(name), bool(inet))
            yield (pid.id, pid)

    def _register_patch(self, name, patch_obj):
        self.patches[name] = patch_obj
        patch_obj.start()

    def setUp(self):
        logging.disable(logging.CRITICAL)

        # выключаем ненужный код
        self._register_patch('hbf_init',
                             unittest.mock.patch('hbf.code.init'))
        self._register_patch('dummy_sections',
                             unittest.mock.patch('hbf.code.FW._init_dummy_sections'))

        # подменяем hosts на self.HOSTS
        self._register_patch('resolve',
                             unittest.mock.patch('socket.getaddrinfo', side_effect=self._getaddrinfo))

        # подменяем макросы на self.MACROSES
        self._register_patch('macroses',
                             unittest.mock.patch('hbf.code.Macroses.data_iter', side_effect=self._macro_iter))

        # не читать router.dnscache.full
        self._register_patch('dns_cache',
                             unittest.mock.patch('hbf.code.DNSCache.data_iter', side_effect=lambda: []))

        # т.к. мы выключили hbf.init
        NO_FORK_LOCK.acquire()
        hbf.Macroses().clear()
        macroses = hbf.Macroses().update()
        hbf.MacroTree.update_all(updated_macroses=macroses)

        hbf.FW().drills = DrillsConfig()
        if self.DRILLS_CONF:
            self._register_patch('drills', self.patch_drills(hbf.FW().drills, self.DRILLS_CONF))

        self._bk_sections = None
        if self.SECTIONS:
            self._bk_sections = hbf.FW().sections
            hbf.FW().sections = self.SECTIONS

        hbf.FW().update_macroses(None)

        hbf.Hosts.cache_clear()
        hbf.Ruleset.cache_clear()

        self.maxDiff = None

    def tearDown(self):
        unittest.mock.patch.stopall()
        self.patches = {}

        if self._bk_sections is not None:
            hbf.FW().sections = self._bk_sections
            self._bk_sections = None

        hbf.Singleton.clear_instances()
        hbf.Ruleset.rendered = dict()
        NO_FORK_LOCK.release()

        show_profileit_results()

        logging.disable(logging.NOTSET)

    def patch_drills(self, drill_config, json_conf, mtime=None):
        client = drill_config.client
        def _download_mock():
            client.content = json_conf
            client.mtime = mtime
            return True
        patch = unittest.mock.patch.object(client, "download", _download_mock)
        patch.start()
        drill_config.update()
        return patch
