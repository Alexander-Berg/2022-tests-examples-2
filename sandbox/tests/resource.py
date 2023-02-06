from __future__ import absolute_import, unicode_literals

import pytest

from sandbox.common.types import resource as ctr


class TestResource(object):

    def test__relpath(self):

        with pytest.raises(ValueError):
            ctr.relpath(0)

        with pytest.raises(ValueError):
            ctr.relpath("")

        assert ctr.relpath(5) == ("00", "5", "5")
        assert ctr.relpath(50) == ("00", "50", "50")
        assert ctr.relpath(503) == ("5", "03", "503")
        assert ctr.relpath(5031) == ("50", "31", "5031")
