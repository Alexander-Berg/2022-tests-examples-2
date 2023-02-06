import pytest

from ipv4mgr.apps.server.api.racktables.errors import Map64InputError
from ipv4mgr.apps.server.api.racktables.handlers import (
    DeleteMap64Request,
    PutMap64Request,
)


class TestPutMap64Request:
    def test_invalid_addr(self):
        with pytest.raises(Map64InputError):
            PutMap64Request.parse_obj({"addr": "bad addr"})

    def test_invalid_net(self):
        with pytest.raises(Map64InputError):
            PutMap64Request.parse_obj({"net": "bad net"})


class TestDeleteMap64Request:
    def test_invalid_addr(self):
        with pytest.raises(Map64InputError):
            DeleteMap64Request.parse_obj({"addr": "bad addr", "net": "0.0.0.0/32"})
