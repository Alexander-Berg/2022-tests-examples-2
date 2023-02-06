import json
import time
from unittest.mock import patch

from . import BaseTest
from hbf.ipaddress2 import ip_network
from hbf.drills import DrillsConfig


def _make_conf(begin, duration, project, location, excludes=None):
    return {
        "begin": str(int(begin)),  # php экспортирует эти поля как строки
        "duration": str(int(duration)),
        "project": project,
        "location": location,
        "exclude": [] if excludes is None else list(excludes),
    }


class TestDrills(BaseTest):
    HOSTS = {
        "testhost1": ["192.168.0.5"],
        "testhost2": ["192.168.0.7"],
    }

    MACROSES = {
        "_PROJ_": [
            "192.168.0.0/24",
        ],
        "_LOC_": [
            "10.0.0.0/8",
            "192.168.0.0/16",
        ],
        "_C_1_": [
            "192.168.0.3",
            "testhost1",
            "testhost2",
            "testhost3",  # not exists
        ],
        "_TRYPO_": [
            "100000/12@2a02:6b8:c00::/40",
            "1234@2a02:6b8:c00::/40",
        ]
    }

    def test1(self):
        "попадание в оба макроса"
        conf = DrillsConfig()
        now = time.time()
        self.patch_drills(conf, json.dumps([_make_conf(now, 1, "_PROJ_", "_LOC_")]))

        self.assertTrue(conf.enabled_for(ip_network("192.168.0.1")))
        self.assertFalse(conf.enabled_for(ip_network("192.168.1.1")))
        self.assertFalse(conf.enabled_for(ip_network("10.0.0.1")))

    def test2(self):
        "попадание во временной интервал"
        conf = DrillsConfig()
        now = time.time()

        self.patch_drills(conf, json.dumps([_make_conf(now - 10, 1, "_PROJ_", "_LOC_")]))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.1")))

        self.patch_drills(conf, json.dumps([_make_conf(now + 10, 1, "_PROJ_", "_LOC_")]))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.1")))

        self.patch_drills(conf, json.dumps([_make_conf(now - 1, 1, "_PROJ_", "_LOC_")]))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.1")))

        self.patch_drills(conf, json.dumps([_make_conf(now, 10, "_PROJ_", "_LOC_")]))
        self.assertTrue(conf.enabled_for(ip_network("192.168.0.1")))

    def test3(self):
        "исключения"
        conf = DrillsConfig()
        now = time.time()

        self.patch_drills(conf, json.dumps([_make_conf(now, 10, "_PROJ_", "_LOC_", [
            "_C_1_",
            "_NOT_EXIST_MACRO_",
            "testhost2",
            "not-exist-host",
            "blah blah!",
            "",
            "192.168.0.16/28",
        ])]))
        self.assertTrue(conf.enabled_for(ip_network("192.168.0.2")))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.3")))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.5")))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.7")))
        self.assertFalse(conf.enabled_for(ip_network("192.168.0.17")))

    def test4(self):
        "обновление конфига"
        conf = DrillsConfig()
        now = time.time()

        self.patch_drills(conf, json.dumps([_make_conf(now, 10, "_PROJ_", "_LOC_")]))
        d1 = sorted(conf.data)
        self.patch_drills(conf, json.dumps([
            _make_conf(now, 10, "_PROJ_", "_LOC_"),
            _make_conf(now + 3600, 10, "_PROJ_", "_LOC_"),
        ]))
        d2 = sorted(conf.data)
        self.assertEqual(2, len(d2))
        self.assertIs(d1[0], d2[0])

        self.patch_drills(conf, json.dumps([]))
        self.assertEqual(0, len(conf.data))

        self.patch_drills(conf, json.dumps([_make_conf(now, 10, "_PROJ_", "_LOC_", ["_C_1_"])]))

        # скачали то же самое, должно вернуть False
        self.assertFalse(conf.update())

        # макросы раскрываются в то же самое
        self.assertFalse(conf.reindex())

        # макросы изменились
        test3_ip = ip_network("192.168.0.9")
        self.assertTrue(conf.enabled_for(test3_ip))
        hosts_copy = dict(self.HOSTS)
        hosts_copy["testhost3"] = [str(test3_ip)]
        with patch.object(self, "HOSTS", hosts_copy):
            self.assertTrue(conf.reindex())
            self.assertFalse(conf.enabled_for(test3_ip))

    def test_last_update_time(self):
        now = int(time.time())
        mtime = now - 60

        def make_drills(begin, duration):
            ret = DrillsConfig()
            self.patch_drills(ret, json.dumps([
                _make_conf(begin, duration, "_PROJ_", "_LOC_"),
            ]), mtime=mtime)

            # эти 2 атрибута просто используются в тестах для читаемости
            ret.begin_time = begin
            ret.end_time = begin + duration
            return ret

        # сначала 0
        conf = DrillsConfig()
        self.assertEqual(0, int(conf.last_update_time))

        # потом - момент начала учений
        conf = make_drills(now, 10)
        self.assertEqual(now, int(conf.last_update_time))

        # если учения прошли - момент окончания учений
        conf = make_drills(now - 30, 10)
        self.assertEqual(now - 20, int(conf.last_update_time))

        # если учения начались и окончились по расписанию
        conf = make_drills(now + 5, 100)
        # до момента начала учений - last_update_time не меняется
        self.assertEqual(0, int(conf.last_update_time))
        with patch("time.time", lambda: conf.begin_time + 1):
            # зато меняется в момент начала
            self.assertEqual(conf.begin_time, int(conf.last_update_time))
        with patch("time.time", lambda: conf.end_time - 1):
            # не меняется с течением учений
            self.assertEqual(conf.begin_time, int(conf.last_update_time))
        with patch("time.time", lambda: conf.end_time):
            # меняется в момент окончания
            self.assertEqual(conf.end_time, int(conf.last_update_time))
        with patch("time.time", lambda: conf.end_time + 1):
            # и остаётся после окончания
            self.assertEqual(conf.end_time, int(conf.last_update_time))
        # учения исчезли из выгрузки через 2 секунды после их окончания
        with patch("time.time", lambda: conf.end_time + 2):
            self.patch_drills(conf, "[]", mtime=conf.end_time + 2)
        with patch("time.time", lambda: conf.end_time + 3):
            # и остаётся после пропадения учений из выгрузки
            self.assertEqual(conf.end_time, int(conf.last_update_time))

    def test_export_for_walle(self):
        conf = DrillsConfig()
        now = int(time.time())
        duration = 100
        self.patch_drills(conf, json.dumps([_make_conf(now, duration, '_PROJ_', '_LOC_', ['_C_1_', '_TRYPO_'])]))

        self.assertEqual(
            [{
                'begin': now,
                'duration': duration,
                'exclude': ['_C_1_', '_TRYPO_'],
                'exclude_ips': ['192.168.0.3', '192.168.0.5', '192.168.0.7', '1234@2a02:6b8:c00::/40', '100000/12@2a02:6b8:c00::/40'],
                'location': '_LOC_',
                'location_ips': ['10.0.0.0/8', '192.168.0.0/16'],
                'project': '_PROJ_',
                'project_ips': ['192.168.0.0/24'],
            }],
            conf.export_for_walle()
        )
