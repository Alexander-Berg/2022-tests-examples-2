from __future__ import division, unicode_literals

import pytest

from sandbox.common import yav


class TestYavSecret(object):

    def test__secret_full(self):
        sec = yav.Secret.create("sec-1234", "ver-9999")
        assert sec.secret_uuid == "sec-1234"
        assert sec.version_uuid == "ver-9999"

    def test__secret_no_version(self):
        assert yav.Secret.create("sec-1234").version_uuid is None

    def test__secret_errors(self):
        with pytest.raises(ValueError):
            yav.Secret.create("foo-1234")
        with pytest.raises(ValueError):
            yav.Secret.create("foo-1234", "bar-1234")
        with pytest.raises(ValueError):
            yav.Secret.create("sec-1234", "bar-1234")

    def test__secret_str(self):
        s1 = yav.Secret.create("sec-1234")
        assert "{}".format(s1) == "sec-1234"
        s2 = yav.Secret.create("sec-1234", "ver-9999")
        assert "{}".format(s2) == "sec-1234@ver-9999"


class TestYavData(object):

    KEY = b"860ef82a836b0adaa9b57f8d7e0166ca"
    TEXT = "foooobaaar"

    def test__encrypt_decrypt(self):
        data = yav.Data(self.TEXT, "ver-9999", None)

        encrypted = data.encrypt(self.KEY)
        assert yav.Data.decrypt(self.KEY, encrypted) == self.TEXT

        with pytest.raises(yav.Data.Error):
            yav.Data({"not", "json", "serialisable"}, "ver-9999", None).encrypt(self.KEY)

        with pytest.raises(yav.Data.Error):
            # invalid JSON encrypted
            yav.Data.decrypt(self.KEY, b"Ti3HOPLH9vo4x9BlKLP34Wj+QP4HDVkfYeWrqbesxhM=")
