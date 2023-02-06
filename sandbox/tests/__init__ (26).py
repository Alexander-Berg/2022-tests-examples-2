# coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest

from sandbox.common import urls
from sandbox.common import config


@pytest.mark.skipif(not config._inside_the_binary(), reason="non-binary tests cannot ensure default settings values")
class TestUrls(object):

    def test__server_url(self):
        cfg = config.Registry()
        assert urls.server_url() == "http://sandbox.yandex-team.ru:8081"
        assert urls.server_url(cfg) == "http://sandbox.yandex-team.ru:8081"
        cfg.server.web.address.show_port = False
        assert urls.server_url(cfg) == "https://sandbox.yandex-team.ru"

    def test__get_task_link(self):
        assert urls.get_task_link(142) == "http://sandbox.yandex-team.ru:8081/task/142"

    def test__get_resource_link(self):
        assert urls.get_resource_link(142) == "http://sandbox.yandex-team.ru:8081/resource/142"

    def test__get_scheduler_link(self):
        assert urls.get_scheduler_link(142) == "http://sandbox.yandex-team.ru:8081/scheduler/142"

    def test__execution_dir_link(self):
        cfg = config.Registry()
        assert urls.execution_dir_link(142) == "http://sandbox.yandex-team.ru:13578/2/4/142"
        assert urls.execution_dir_link(142, cfg) == "http://sandbox.yandex-team.ru:13578/2/4/142"
        cfg.client.fileserver.proxy.host = "foo.bar"
        assert urls.execution_dir_link(142, cfg) == "https://foo.bar/task/142"
