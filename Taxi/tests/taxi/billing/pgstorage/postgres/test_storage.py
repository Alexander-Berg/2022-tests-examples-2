import random

import pytest

from taxi.billing.pgstorage import storage


async def test_storage_vshard_from_id_valid():
    for i in range(
            0,
            storage.Storage.MAX_VSHARD_ID + 1,
            random.randint(1, storage.Storage.MAX_VSHARD_ID),
    ):
        assert storage.Storage.vshard_from_id(1000000 + i) == i


async def test_storage_vshard_from_id_invalid():
    with pytest.raises(ValueError):
        assert storage.Storage.vshard_from_id(-1000000)

    with pytest.raises(ValueError):
        assert storage.Storage.vshard_from_id(1000256)
