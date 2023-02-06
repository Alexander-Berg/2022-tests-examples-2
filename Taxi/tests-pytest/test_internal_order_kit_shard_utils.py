import uuid

import pytest

from taxi.internal.order_kit import shard_utils


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('obj_id,expected', [
    ('f2c39c5cdd0911e885a860f81db02486', 0x05),
    ('2dfaad6c89e5487bae26061eb8600f55', 0x00),
    ('ef2f637d50f5ef24b4f19752f51ad33c', 0xa),
    ('3aec0f44-881d-bd47-b078-46c4ee61c003', 0x0f),
    ('invalid_uuid', 0x00),
])
def test_get_shard_id(obj_id, expected):
    result = shard_utils.get_shard_id(obj_id)
    assert result == expected


def _generate_set_shard_id_tests():
    tests = []

    obj_ids = (
        uuid.UUID('2dfaad6c89e5487bae26061eb8600f55'),
        uuid.UUID('07f1d3dd-0dc9-4d95-8981-ce6a76b17a7a'),
    )
    for shard_id in xrange(shard_utils.SHARD_ID_MAX + 1):
        for obj_id in obj_ids:
            tests.append((obj_id, shard_id))

    return tests


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('obj_id,shard_id', _generate_set_shard_id_tests())
def test_set_shard_id(obj_id, shard_id):
    new_obj_id = shard_utils.set_shard_id(obj_id, shard_id)
    assert shard_utils.get_shard_id(new_obj_id.hex) == shard_id
