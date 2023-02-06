import pytest

from taxi.util import order_shards


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'obj_id,expected',
    [
        ('f2c39c5cdd0911e885a860f81db02486', 0x05),
        ('2dfaad6c89e5487bae26061eb8600f55', 0x00),
        ('ef2f637d50f5ef24b4f19752f51ad33c', 0xA),
        ('3aec0f44-881d-bd47-b078-46c4ee61c003', 0x0F),
        ('invalid_uuid', 0x00),
    ],
)
def test_get_shard_id(obj_id, expected):
    result = order_shards.get_shard_id(obj_id)
    assert result == expected
