from __future__ import absolute_import, unicode_literals

from sandbox.common.types import database as ctd


class TestDatabase(object):

    def test__readpreference(self):
        assert set(ctd.ReadPreference) == {"default", "readonly", "preferred"}
