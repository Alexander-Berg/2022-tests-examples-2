from datetime import datetime
from unittest import mock

import freezegun
import pytest

from settings import Settings
from checkist.patches.patch import Patch
from checkist.patches.service import PatchesService, AnnInstance


class TestPatchesService:

    @pytest.fixture
    def db(self):
        res = mock.Mock()
        res.insert_many = mock.AsyncMock()
        res.find_one = mock.AsyncMock()
        return res

    @pytest.fixture
    def ck(self):
        res = mock.Mock()
        res.session().__aenter__ = mock.AsyncMock()
        res.session().__aexit__ = mock.AsyncMock()
        return res

    @pytest.fixture
    def devs(self):
        res = mock.AsyncMock()
        res.search.return_value = {12345: mock.Mock(vendor="huawei")}
        return res

    @pytest.fixture
    def ann(self):
        res = mock.AsyncMock(AnnInstance)
        return res

    @pytest.mark.asyncio
    @freezegun.freeze_time("2020-01-01")
    async def test_deploy(self, db, ck, devs):
        db.insert_many.return_value.inserted_ids = ["my_id"]
        patch = Patch("noc-sas", "my patch", [], "a7446e8c318d900d4fe0c349aaaa4754", 123456, 654321, None)

        service = PatchesService(db, ck, devs, Settings())
        res = await service.deploy(None, "NOCRFCS-1234", patch)

        db.insert_many.assert_called_once_with([{
            "createdAt": datetime(2020, 1, 1, 0, 0, 0),
            "hostname": "noc-sas",
            "config_md5": "a7446e8c318d900d4fe0c349aaaa4754",
        }])

        ck_deploy = ck.session().__aenter__.return_value.deploy
        ck_deploy.assert_called_once_with({"my_id": patch}, None, "NOCRFCS-1234")
        assert res == ck_deploy.return_value
