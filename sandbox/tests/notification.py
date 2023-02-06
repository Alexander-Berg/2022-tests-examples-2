from __future__ import absolute_import, unicode_literals

from sandbox.common.types import notification as ctn


class TestNotification(object):

    def test__transport(self):
        assert set(ctn.Transport) == {"q", "telegram", "email", "juggler"}
