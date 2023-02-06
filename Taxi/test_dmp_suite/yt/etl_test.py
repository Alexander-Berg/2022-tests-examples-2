import pytest
import mock
import datetime

from dmp_suite.yt import (
    etl,
    YTMeta,
    String,
    resolve_meta,
    COMPRESSION_ATTRIBUTES,
    YTTable,
    BUFFER_TABLE_TTL,
    ROTATION_TABLE_TTL,
    Int,
    operation as yt)
from connection.yt import get_yt_client

from test_dmp_suite.yt import utils


class TestTable(YTTable):
    __unique_keys__ = True

    id = String(sort_key=True, sort_position=0)
    name = String()


test_table = utils.fixture_random_yt_table(TestTable)


class TestHeaviestTable(YTTable):
    __unique_keys__ = True
    __compression_level__ = 'heaviest'

    id = String(sort_key=True, sort_position=0)
    name = String()


test_heaviest_table = utils.fixture_random_yt_table(TestHeaviestTable)


_TABLE_OR_META = [
    pytest.param(lambda table: table, id="table"),
    pytest.param(lambda table: YTMeta(table), id="meta")
]


_test_data = [
    dict(id='1', name='hello'),
    dict(id='2', name='world'),
    dict(id='3', name='!!!')
]


@pytest.mark.slow
def test_write_buffer(test_table):
    meta = YTMeta(test_table)
    data = _test_data[:2]
    etl.write_buffer(meta, data)
    path = meta.buffer_path()
    assert get_yt_client().exists(path)

    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data

    data = _test_data[2:]
    etl.write_buffer(meta, data)
    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data


@pytest.mark.slow
def test_write_unordered_buffer(test_table):
    meta = YTMeta(test_table)
    data = [_test_data[1], _test_data[0], _test_data[2]]
    path = meta.buffer_path()
    etl.write_buffer(meta, data)
    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data


@pytest.mark.slow
def test_write_duplicate_buffer(test_table):
    meta = YTMeta(test_table)
    data = [_test_data[0], _test_data[0]]
    path = meta.buffer_path()
    etl.write_buffer(meta, data)
    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data


@pytest.mark.slow
def test_write_rotation(test_table):
    meta = YTMeta(test_table)
    data = _test_data[:2]
    etl.write_rotation(meta, data)
    path = meta.rotation_path()
    assert get_yt_client().exists(path)

    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data

    data = _test_data[2:]
    etl.write_rotation(meta, data)
    yt_data = list(get_yt_client().read_table(path))
    assert data == yt_data


@pytest.mark.slow
def test_write_unordered_rotation(test_table):
    meta = YTMeta(test_table)
    with pytest.raises(Exception):
        etl.write_rotation(
            meta,
            [_test_data[1], _test_data[0], _test_data[2]]
        )


@pytest.mark.slow
def test_write_duplicate_rotation(test_table):
    meta = YTMeta(test_table)
    with pytest.raises(Exception):
        etl.write_rotation(
            meta,
            [_test_data[0], _test_data[0]]
        )


@pytest.mark.slow
@pytest.mark.parametrize("table_processor", _TABLE_OR_META)
def test_rotation_to_target(table_processor, test_table):
    table = table_processor(test_table)
    meta = resolve_meta(test_table)
    path = meta.target_path()

    etl.write_rotation(meta, _test_data)
    etl.rotation_to_target(table)
    yt_data = list(get_yt_client().read_table(path))
    assert _test_data == yt_data
    assert not get_yt_client().exists(meta.rotation_path())
    attributes = get_yt_client().get(path + '/@')
    assert 'expiration_time' not in attributes


@pytest.mark.slow
@pytest.mark.parametrize("table_processor", _TABLE_OR_META)
@mock.patch('dmp_suite.yt.meta.dtu.utcnow', return_value=datetime.datetime(2030, 1, 1))
def test_init_buffer_table(mocked_dtu_msknow, table_processor, test_table):
    table = table_processor(test_table)
    meta = resolve_meta(test_table)
    path = meta.buffer_path()

    assert not get_yt_client().exists(path)
    etl.init_buffer_table(table)
    assert get_yt_client().exists(path)
    assert mocked_dtu_msknow.called
    attributes = get_yt_client().get(path + '/@')
    assert_ttl(attributes, datetime.datetime(2030, 1, 1) + BUFFER_TABLE_TTL)


@pytest.mark.slow
@pytest.mark.parametrize("table_processor", _TABLE_OR_META)
@mock.patch('dmp_suite.yt.meta.dtu.utcnow', return_value=datetime.datetime(2030, 1, 1))
def test_init_rotation_table(mocked_dtu_msknow, table_processor, test_table):
    table = table_processor(test_table)
    meta = resolve_meta(test_table)
    path = meta.rotation_path()

    assert not get_yt_client().exists(path)
    etl.init_rotation_table(table)
    assert get_yt_client().exists(path)
    attributes = get_yt_client().get(path + '/@')
    assertCorrectCompressionAttributes(attributes, meta)
    assert mocked_dtu_msknow.called
    assert_ttl(attributes, datetime.datetime(2030, 1, 1) + ROTATION_TABLE_TTL)


@pytest.mark.slow
def test_init_heaviest_rotation_table(test_heaviest_table):
    meta = resolve_meta(test_heaviest_table)
    path = meta.rotation_path()

    etl.init_rotation_table(test_heaviest_table)
    attributes = get_yt_client().get(path + '/@')
    assertCorrectCompressionAttributes(attributes, meta)


@pytest.mark.slow
@pytest.mark.parametrize("table_processor", _TABLE_OR_META)
def test_init_target_table(table_processor, test_table):
    table = table_processor(test_table)
    meta = resolve_meta(test_table)
    path = meta.target_path()

    assert not get_yt_client().exists(path)
    etl.init_target_table(table)
    assert get_yt_client().exists(path)


def assertCorrectCompressionAttributes(attributes, meta):
    expected_attributes = COMPRESSION_ATTRIBUTES[meta.compression_level]
    for attribute, expected_value in expected_attributes.items():
        assert attributes[attribute] == expected_value


def assert_ttl(attributes, expected_ttl):
    current_ttl = attributes['expiration_time']
    assert current_ttl
    assert datetime.datetime.strptime(current_ttl[:19], '%Y-%m-%dT%H:%M:%S') == expected_ttl


@pytest.mark.slow
def test_temporary_buffer_table():
    class Table(YTTable):
        a = Int()
        b = String()

    with etl.temporary_buffer_table(Table) as path:
        assert yt.yt_path_exists(path)
    assert not yt.yt_path_exists(path)
