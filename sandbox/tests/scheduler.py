from __future__ import absolute_import, unicode_literals

from sandbox.common.types import scheduler as cts


class TestScheduler(object):

    def test__status(self):
        assert set(cts.Status) == {"STOPPED", "WATCHING", "WAITING", "FAILURE", "DELETED"}
