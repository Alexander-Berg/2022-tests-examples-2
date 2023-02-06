import uuid

import pytest

from taxi import config
from taxi.internal.order_kit import order_shards
from taxi.internal.order_kit import shard_utils


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('order_id,expected_shard_id', [
    ('f2c39c5cdd0911e885a860f81db02486', 0x05),
    ('2dfaad6c89e5487bae26061eb8600f55', 0x00),
    ('ef2f637d50f5ef24b4f19752f51ad33c', 0xa),
    ('3aec0f44-881d-bd47-b078-46c4ee61c003', 0x0f),
    ('invalid_uuid', 0x00),
])
def test_generate_id_with_shard(order_id, expected_shard_id):
    result = order_shards.generate_id_with_shard(order_id)

    assert (
        shard_utils.get_shard_id(order_id) ==
        shard_utils.get_shard_id(result) ==
        expected_shard_id
    )


@pytest.mark.parametrize('shards,expected_shard_id', [
    ([], 0),
    ([10], 10),
])
@pytest.inline_callbacks
def test_generate_order_id(shards, expected_shard_id):
    yield config.ORDER_SHARDS.save(shards)
    order_id, shard_id = yield order_shards.generate_order_id()

    assert isinstance(order_id, basestring)
    uuid.UUID(order_id)
    actual_shard_id = shard_utils.get_shard_id(order_id)
    assert actual_shard_id == expected_shard_id
    assert actual_shard_id == shard_id
    if shards:
        assert actual_shard_id in shards
