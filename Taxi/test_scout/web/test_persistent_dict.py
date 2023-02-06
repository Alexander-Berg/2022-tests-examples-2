import os

from scout import persistent_storage
from test_scout.web import persistent_storage_utils

PersistentComponent = persistent_storage_utils.PersistentComponent
# pylint: disable=invalid-name
make_persistent_component = persistent_storage_utils.make_persistent_component

PersistentDict = persistent_storage.PersistentDict


async def test_pers_dict_dump(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key', storage)
        data.set('key1', 'value')
        assert data.is_actual('key1')
        assert not data.is_fallback('key1')

        data.set('key2', 42)
        assert data.is_actual('key2')
        assert not data.is_fallback('key2')
        assert data.get('key2') == 42

        assert data.get('key1') == 'value'

    assert os.path.exists(PersistentComponent.get_dump_file_path(storage_dir))

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key', storage)
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')
        assert data.get('key1') == 'value'
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')

        assert not data.is_actual('key2')
        assert data.is_fallback('key2')
        assert data.get('key2') == 42
        assert not data.is_actual('key2')
        assert data.is_fallback('key2')


async def test_pers_dict_set_actual(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key', storage)
        data.set('key1', 'value')
        assert data.is_actual('key1')
        assert not data.is_fallback('key1')
        data.set_actual('key1', False)
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')

        data.set('key2', 42)
        assert data.is_actual('key2')
        assert not data.is_fallback('key2')
        assert data.get('key2') == 42
        data.set_actual('key2', False)
        assert not data.is_actual('key2')
        assert data.is_fallback('key2')

        assert data.get('key1') == 'value'

    assert os.path.exists(PersistentComponent.get_dump_file_path(storage_dir))

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key', storage)
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')
        assert data.get('key1') == 'value'
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')
        data.set_actual('key1', True)
        assert data.is_actual('key1')
        assert not data.is_fallback('key1')

        assert not data.is_actual('key2')
        assert data.is_fallback('key2')
        assert data.get('key2') == 42
        assert not data.is_actual('key2')
        assert data.is_fallback('key2')
        data.set_actual('key2', True)
        assert data.is_actual('key2')
        assert not data.is_fallback('key2')


async def test_pers_dict_rewrite(storage_dir):
    async with make_persistent_component(storage_dir) as storage:
        data1 = PersistentDict('test_key1', storage)
        data1.set('key1', 'value')
        data1.set('key2', 42)
        assert data1.get('key1') == 'value'
        assert data1.get('key2') == 42

        data2 = PersistentDict('test_key2', storage)
        data2.set('key1', '2value')
        data2.set('key2', 242)
        assert data2.get('key1') == '2value'
        assert data2.get('key2') == 242

    async with make_persistent_component(storage_dir) as storage:
        data1 = PersistentDict('test_key1', storage)
        assert data1.get('key1') == 'value'
        assert data1.get('key2') == 42

        data2 = PersistentDict('test_key2', storage)
        assert data2.get('key1') == '2value'
        assert data2.get('key2') == 242

        assert not data1.is_actual('key1')
        assert data1.is_fallback('key1')
        data1.set('key1', '3value')
        assert data1.is_actual('key1')
        assert not data1.is_fallback('key1')

        assert not data1.is_actual('key2')
        assert data1.is_fallback('key2')
        data1.set('key2', 342)
        assert data1.is_actual('key2')
        assert not data1.is_fallback('key2')

    async with make_persistent_component(storage_dir) as storage:
        data1 = PersistentDict('test_key1', storage)
        assert data1.get('key1') == '3value'
        assert not data1.is_actual('key1')
        assert data1.is_fallback('key1')

        assert data1.get('key2') == 342
        assert not data1.is_actual('key2')
        assert data1.is_fallback('key2')

        data2 = PersistentDict('test_key2', storage)
        assert data2.get('key1') == '2value'
        assert not data2.is_actual('key1')
        assert data2.is_fallback('key1')

        assert data2.get('key2') == 242
        assert not data2.is_actual('key2')
        assert data2.is_fallback('key2')


async def test_pers_dict_get_does_not_update(storage_dir):
    content = {'nested': 42}

    async with make_persistent_component(storage_dir) as storage:
        PersistentDict('test_key1', storage).set('key1', content)

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key1', storage)
        assert data.get('key1') == content
        assert not data.is_actual('key1')
        assert data.is_fallback('key1')
        data.get('key1')['nested'] = 43
        assert 'nested2' not in data
        assert data.get('nested2') is None

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key1', storage)
        assert data.get('key1') == content
        assert 'nested2' not in data


async def test_pers_dict_erase(storage_dir):
    content = {'nested': 42}

    async with make_persistent_component(storage_dir) as storage:
        PersistentDict('test_key1', storage).set('key1', content)

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key1', storage)
        assert 'key1' in data
        assert data.get('key1') == content
        assert data.erase('key1')
        assert not data.is_actual('key1')
        assert not data.erase('key1')
        assert not data.is_actual('key1')

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key1', storage)
        assert 'key1' not in data
        assert not data.is_actual('key1')

        # Erasing actual data
        data.set('key1', content)
        assert data.is_actual('key1')
        assert not data.is_fallback('key1')
        assert data.erase('key1')
        assert not data.is_actual('key1')

    async with make_persistent_component(storage_dir) as storage:
        data = PersistentDict('test_key1', storage)
        assert 'key1' not in data
        assert not data.is_actual('key1')
