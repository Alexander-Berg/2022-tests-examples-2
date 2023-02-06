from passport.infra.daemons.yasmsapi.tools.keys_generator.src.utils import (
    add_key,
    update_keys,
)


def check_key(key, key_id, key_time):
    assert key['id'] == key_id
    assert key['create_ts'] == key_time
    assert len(bytes.fromhex(key['body'])) == 32


def check_keys(keys_list, length, last_id, last_time):
    assert len(keys_list) == length
    check_key(keys_list[-1], last_id, last_time)


def test_add_key():
    keys = []

    assert 1 == add_key(keys, 12345)
    check_keys(keys, 1, 1, 12345)

    assert 2 == add_key(keys, 111)
    check_keys(keys, 2, 2, 111)

    keys.append(
        {
            'id': 12345,
            'create_ts': 123456789,
            'body': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
        }
    )

    assert 12346 == add_key(keys, 1)
    check_keys(keys, 4, 12346, 1)

    check_key(keys[0], 1, 12345)
    check_key(keys[1], 2, 111)
    check_key(keys[2], 12345, 123456789)
    check_key(keys[3], 12346, 1)


def test_update_keys():
    keys = []

    # empty and don't need new key
    keys, added, deleted = update_keys(keys, 100, 1000, 100)

    assert added == []
    assert deleted == []
    assert len(keys) == 0

    # empty and need new key
    keys, added, deleted = update_keys(keys, 100, 1000, 1000)

    assert added == [1]
    assert deleted == []
    assert len(keys) == 1
    check_key(keys[0], 1, 1000)

    # need another key
    keys, added, deleted = update_keys(keys, 100, 1000, 2000)

    assert added == [2]
    assert deleted == []
    assert len(keys) == 2
    check_key(keys[0], 1, 1000)
    check_key(keys[1], 2, 2000)

    # don't need another key
    keys, added, deleted = update_keys(keys, 100, 1000, 2999)

    assert added == []
    assert deleted == []
    assert len(keys) == 2
    check_key(keys[0], 1, 1000)
    check_key(keys[1], 2, 2000)

    # need another key and delete oldest one
    keys, added, deleted = update_keys(keys, 2, 1000, 3000)

    assert added == [3]
    assert deleted == [1]
    assert len(keys) == 2
    check_key(keys[0], 2, 2000)
    check_key(keys[1], 3, 3000)

    # no change
    keys, added, deleted = update_keys(keys, 2, 1000, 3100)

    assert added == []
    assert deleted == []
    assert len(keys) == 2
    check_key(keys[0], 2, 2000)
    check_key(keys[1], 3, 3000)

    # need to delete more
    keys, added, deleted = update_keys(keys, 1, 1000, 3200)

    assert added == []
    assert deleted == [2]
    assert len(keys) == 1
    check_key(keys[0], 3, 3000)
