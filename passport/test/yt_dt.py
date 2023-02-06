# -*- coding: utf-8 -*-

import mock


class FakeYtDt(object):
    def __init__(self):
        self._mock = mock.Mock()
        self._mount_mock = mock.Mock()
        self._patch = mock.patch(
            'yt.wrapper.YtClient.select_rows',
            self._mock,
        )
        self._patch_mount = mock.patch(
            'yt.wrapper.YtClient.mount_table',
            self._mount_mock,
        )

    def set_response_value(self, value):
        self._mock.return_value = value

    def set_response_side_effect(self, exc):
        self._mock.side_effect = exc

    def start(self):
        self._patch.start()
        self._patch_mount.start()

    def stop(self):
        self._patch_mount.stop()
        self._patch.stop()
