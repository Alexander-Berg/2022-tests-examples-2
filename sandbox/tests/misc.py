from __future__ import absolute_import, unicode_literals

import pytest

from sandbox.common.types import misc as ctm


class TestMisc(object):

    def test__interface(self):
        assert set(ctm.Interface) == {"old", "new"}

    def test__notexists(self):
        assert not bool(ctm.NotExists)
        assert not ctm.NotExists
        assert ctm.NotExists is not None
        assert ctm.NotExists != 0
        assert ctm.NotExists == ctm.NotExists

    @pytest.mark.parametrize(
        "cls",
        (ctm.Upload.Check, ctm.Upload.Prepare, ctm.Upload.DataTransfer, ctm.Upload.Share)
    )
    def test__upload_state(self, cls):
        obj = cls()
        assert cls.__name__ in repr(obj)

        for attr in cls.__slots__:
            assert hasattr(obj, attr)
