import asyncio
import dataclasses
import os

import pytest

from test_scout.web import persistent_storage_utils


BROKEN_DUMP1 = """
tvm_name_to_endpoints:
  envoy-exp-alpha: !!python/object:some.object.that.does.not.Exist
    endpoints: []
"""


PersistentComponent = persistent_storage_utils.PersistentComponent
# pylint: disable=invalid-name
make_persistent_component = persistent_storage_utils.make_persistent_component
TEST_DUMP_INTERVAL_SEC = persistent_storage_utils.TEST_DUMP_INTERVAL_SEC


@dataclasses.dataclass(frozen=True)
class HostPortZoneAge:
    host: str
    port: int
    zone: str
    age: int


async def test_path(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        assert storage.get_dump_version_dirname() == 'v1'
        assert storage.get_dump_prev_version_dirname() is None
        assert storage.get_dump_filename() == 'ps_instance_0.yaml'

    async with make_persistent_component(
            storage_dir, version=3, prev_version=2,
    ) as storage:
        assert storage.get_dump_version_dirname() == 'v3'
        assert storage.get_dump_prev_version_dirname() == 'v2'


async def test_dump(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        content = {'key1': 'value', 'key2': 42}
        storage.store('test_key', content)
        assert storage.get('test_key') == content

    assert os.path.exists(PersistentComponent.get_dump_file_path(storage_dir))

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content


async def test_auto_dump(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        content = {'key1': 'the value', 'the key2': 42}
        storage.store('test_key', content)

        content2 = {'2key1': 'value', '2key2': 42}
        storage.store('test_key2', content2)

        dump_path = PersistentComponent.get_dump_file_path(storage_dir)

        for _ in range(10):
            await asyncio.sleep(TEST_DUMP_INTERVAL_SEC)
            if os.path.exists(dump_path):
                break

        assert os.path.exists(dump_path)

        async with make_persistent_component(storage_dir) as validator:
            assert validator.get('test_key') == content
            assert validator.get('test_key2') == content2


async def test_rewrite(storage_dir):
    content = {'key1': 'the value', 'the key2': 42}
    content2 = {'2key1': 'value', '2key2': 42}

    async with make_persistent_component(storage_dir) as storage:
        storage.store('test_key', content)
        storage.store('test_key2', content2)

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content
        assert storage.get('test_key2') == content2
        storage.store('test_key', content2)
        storage.store('test_key2', content)

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content2
        assert storage.get('test_key2') == content


async def test_multiple_starts(storage_dir):
    content = {'key1': {'nested': 42}}

    async with make_persistent_component(storage_dir) as storage:
        storage.store('test_key', content)

    # Checking that first and following loads have cache data
    for _ in range(2):
        async with make_persistent_component(storage_dir) as storage:
            assert storage.get('test_key') == content


async def test_get_does_not_update(storage_dir):
    content = {'key1': {'nested': 42}}

    async with make_persistent_component(storage_dir) as storage:
        storage.store('test_key', content)

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content
        storage.get('test_key')['key1']['nested'] = 43
        storage.get('test_key')['nested2'] = 44

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key')['key1']['nested'] == 42
        assert 'nested2' not in storage.get('test_key')


async def test_update(storage_dir):
    content = {'key1': {'nested': 42}}

    async with make_persistent_component(storage_dir) as storage:
        storage.store('test_key', content)

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content
        storage.get_for_update('test_key')['nested'] = 43

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key')['nested'] == 43


async def test_complex_data(storage_dir):
    content = {'key1': HostPortZoneAge(host='a', port=1, zone='b', age=2)}

    async with make_persistent_component(storage_dir) as storage:
        storage.store('test_key', content)

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key') == content
        storage.get_for_update('test_key')['nested'] = 43

    async with make_persistent_component(storage_dir) as storage:
        assert storage.get('test_key')['nested'] == 43


async def test_mismatch_version(storage_dir):
    content = {'key1': 'the value', 'the key2': 42}
    content2 = {'2key1': 'value', '2key2': 42}

    async with make_persistent_component(storage_dir, version=9) as storage:
        storage.store('test_key', content)
        storage.store('test_key2', content2)

    async with make_persistent_component(storage_dir, version=1) as storage:
        assert not storage.get('test_key')
        assert not storage.get('test_key2')
        storage.store('test_key', content2)
        storage.store('test_key2', content)

    async with make_persistent_component(storage_dir, version=1) as storage:
        assert storage.get('test_key') == content2
        assert storage.get('test_key2') == content


@pytest.mark.parametrize(
    'dump_str', [BROKEN_DUMP1], ids=['broken type in payload 1'],
)
async def test_broken_dump(storage_dir, dump_str):
    dump_path = PersistentComponent.get_dump_file_path(storage_dir)

    # create version subdir
    os.makedirs(os.path.dirname(dump_path))

    with open(dump_path, 'w') as dump:
        dump.write(dump_str)

    async with make_persistent_component(storage_dir) as storage:
        assert not storage.get('tvm_name_to_endpoints')


async def test_rm_old_versions(storage_dir):
    path = storage_dir

    async with make_persistent_component(path, version=1) as storage:
        storage.store('schema_1', 1)

    async with make_persistent_component(
            path, version=2, prev_version=1,
    ) as storage:
        storage.store('schema_2', 2)

    async with make_persistent_component(
            path, version=1, prev_version=2,
    ) as storage:
        assert storage.get('schema_1') == 1
        assert storage.get('schema_2') is None

    async with make_persistent_component(
            path, version=2, prev_version=1,
    ) as storage:
        assert storage.get('schema_1') is None
        assert storage.get('schema_2') == 2

    async with make_persistent_component(path, version=3, prev_version=2):
        assert not os.path.exists(
            os.path.dirname(
                PersistentComponent.get_dump_file_path(path, version=1),
            ),
        )

    async with make_persistent_component(path, version=3):
        assert not os.path.exists(
            os.path.dirname(
                PersistentComponent.get_dump_file_path(path, version=2),
            ),
        )
