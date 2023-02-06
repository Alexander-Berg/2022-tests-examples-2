from __future__ import absolute_import, unicode_literals

from sandbox.common.types import user as ctu


class TestUser(object):

    def test__rights(self):
        assert ctu.Rights.get(True) == ctu.Rights.WRITE
        assert ctu.Rights.get(False) == ctu.Rights.READ
