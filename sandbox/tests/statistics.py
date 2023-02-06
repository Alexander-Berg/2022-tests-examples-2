from __future__ import absolute_import, unicode_literals

from sandbox.common.types import statistics as cts


class TestStatistics(object):

    def test__operationtype(self):
        assert list(cts.OperationType) == ["hg", "svn", "rest", "aapi", "docker"]
