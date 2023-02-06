# coding: utf-8

import time

from . import _create_client

import common.types.client as ctc


class TestClientManager:

    hosts = ["__test_host_1", "__test_host_2", "__test_host_3"]
    archs = ["linux", "freebsd", "linux"]
    ncpu = [32, 24, 16]
    ram = [63504, 64398, 128911]
    model = ["e5-2660", "e5620", "e5645"]
    freespace = [522616, 355611, 351080]
    _update_ts = int(time.time())
    update_ts = [_update_ts - 1000, _update_ts - 2000, _update_ts - 3000]
    task_types = ["__TASK_TYPE_1", "__TASK_TYPE_2", "__TASK_TYPE_3", "__TASK_TYPE_4"]
    test_tags = str(
        (
            ctc.Tag.CUSTOM_AUTOCHECK | ctc.Tag.GENERIC |
            (ctc.Tag.SSD & ~ctc.Tag.CUSTOM_NORAMDRIVE)
        ) &
        (ctc.Tag.LINUX_PRECISE | ctc.Tag.LINUX_TRUSTY) &
        (~ctc.Tag.OXYGEN | ctc.Tag.ACCEPTANCE)
    )

    def test_base_actions(self, client_manager):
        for host in self.hosts:
            _create_client(client_manager, host)

        all_clients = client_manager.list()
        assert len(all_clients) == 3

        for i, client in enumerate(all_clients):
            client.arch = self.archs[i]
            client.ncpu = self.ncpu[i]
            client.ram = self.ram[i]
            client.model = self.model[i]
            client.freespace = self.freespace[i]
            client.update_ts = self.update_ts[i]
            client_manager.update(client)

        clients = client_manager.list(hostname=self.hosts[1:])
        assert len(clients) == 2

        clients = client_manager.list(freespace=360000)
        assert len(clients) == 1

        clients = client_manager.list(freespace=-360000)
        assert len(clients) == 2

        clients = client_manager.list(model=self.model[1])
        assert len(clients) == 1

        clients = client_manager.list(model=self.model[1:])
        assert len(clients) == 2
        # проверка для "order by"
        assert clients[1].hostname == self.hosts[2]

        clients = client_manager.list(arch='freebsd')
        assert len(clients) == 1

        clients = client_manager.list(arch='linux')
        assert len(clients) == 2

        clients = client_manager.list(update_ts=self._update_ts)
        assert len(clients) == 0

        clients = client_manager.list(update_ts=-self._update_ts)
        assert len(clients) == 3

        clients = client_manager.list(ncpu=25)
        assert len(clients) == 1

        clients = client_manager.list(ncpu=-25)
        assert len(clients) == 2

        clients = client_manager.list(ram=100000)
        assert len(clients) == 1

        clients = client_manager.list(ram=-100000)
        assert len(clients) == 2

    def test_match_tags(self, client_manager):
        client_platform = "linux_ubuntu_14.04_trusty"
        client = _create_client(client_manager, "__lxc_match_tags")
        client_tags = (ctc.Tag.GENERIC, ctc.Tag.IPV4, ctc.Tag.LINUX_TRUSTY, ctc.Tag.LXC, ctc.Tag.SSD)
        client.update_tags(client_tags, client.TagsOp.SET)
        assert client.match_tags("LINUX_LUCID") == "linux_ubuntu_10.04_lucid"
        assert client.match_tags("LINUX_TRUSTY") == "linux_ubuntu_14.04_trusty"
        assert client.match_tags(
            "~LINUX_PRECISE & ~LINUX_LUCID & ~LINUX_XENIAL & ~LINUX_BIONIC & ~LINUX_FOCAL", None
        ) == client_platform
        assert client.match_tags("CUSTOM_FOOBAR", "linux_ubuntu_12.04_precise") is None
        assert client.match_tags("GENERIC", "osx_10.10_yosemite") is None
        assert client.match_tags("LINUX") == "linux_ubuntu_12.04_precise"
        assert client.match_tags("GENERIC") == "linux_ubuntu_12.04_precise"
        assert client.match_tags("GENERIC", "linux") == "linux_ubuntu_12.04_precise"
        assert client.match_tags("LINUX_XENIAL") == "linux_ubuntu_16.04_xenial"
        assert client.match_tags("LINUX_BIONIC") == "linux_ubuntu_18.04_bionic"
        assert client.match_tags("LINUX_FOCAL") == "linux_ubuntu_20.04_focal"
        assert client.match_tags("LINUX_XENIAL & HDD") is None
        assert client.match_tags("LINUX_XENIAL & HDD", only_detect_platform=True) == "linux_ubuntu_16.04_xenial"

        client = _create_client(client_manager, "__nolxc_match_tags")
        client_tags = (ctc.Tag.GENERIC, ctc.Tag.IPV4, ctc.Tag.LINUX_TRUSTY, ctc.Tag.SSD)
        client.update_tags(client_tags, client.TagsOp.SET)
        assert client.match_tags("GENERIC") == client_platform
        assert client.match_tags("LINUX") == client_platform
        assert client.match_tags("LINUX_PRECISE") is None
        assert client.match_tags("GENERIC", "linux") == client_platform
        assert client.match_tags("CYGWIN | LINUX_PRECISE | LINUX_TRUSTY") == client_platform
        assert client.match_tags("GENERIC", "osx_10.10_yosemite") is None
        assert client.match_tags("CUSTOM_FOOBAR") is None
        assert client.match_tags("LINUX_TRUSTY") == client_platform
        assert client.match_tags("LINUX_TRUSTY & HDD") is None
        assert client.match_tags("LINUX_TRUSTY & HDD", only_detect_platform=True) == client_platform

        client_platform = "osx_10.12_sierra"
        client = _create_client(client_manager, "__mac")
        client_tags = (ctc.Tag.GENERIC, ctc.Tag.IPV4, ctc.Tag.OSX_SIERRA)
        client.update_tags(client_tags, client.TagsOp.SET)
        assert client.match_tags("GENERIC") is None
        assert client.match_tags("CYGWIN | LINUX_PRECISE | LINUX_TRUSTY | OSX") == client_platform
        assert client.match_tags("CYGWIN | LINUX_PRECISE | LINUX_TRUSTY | OSX_SIERRA") == client_platform
        assert client.match_tags("CYGWIN | LINUX_PRECISE | LINUX_TRUSTY | OSX_YOSEMITE") is None
        assert client.match_tags("GENERIC", "osx") == client_platform
        assert client.match_tags("GENERIC", "osx_10.12_sierra") == client_platform
        assert client.match_tags("GENERIC", "osx_10.10_yosemite") is None
        assert client.match_tags("CUSTOM_FOOBAR") is None
        client.update_tags([ctc.Tag.CUSTOM_FOOBAR], client.TagsOp.ADD)
        assert client.match_tags("GENERIC") is None
        assert client.match_tags("CUSTOM_FOOBAR") == client_platform

    def test_match_tags_performance(self, client_manager):
        client_platform = "linux_ubuntu_14.04_trusty"
        client_tags = (ctc.Tag.GENERIC, ctc.Tag.IPV4, ctc.Tag.LINUX_TRUSTY, ctc.Tag.LXC)
        client = _create_client(client_manager, "__match_tags_perf", platform=client_platform)
        client.update_tags(client_tags, client.TagsOp.SET)

        # using tags from AUTOCHECK_BUILD_YA
        tags = self.test_tags
        start = time.time()

        for i in xrange(1000):
            client.match_tags(tags, "linux")

        total_time = time.time() - start
        assert total_time < 1, total_time
