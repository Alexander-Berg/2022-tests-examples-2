import uuid
from typing import Type, Optional

import mock
import pytest

from connection.yt import Pool, get_pool_value
from dmp_suite.yt.maintenance.merge_compress.common import PartitionNode
from dmp_suite.yt.maintenance.merge_compress.content_revision_operation import (
    get_dmp_content_revision, get_content_revision,
    DMP_MERGE_CONTENT_REVISION, CONTENT_REVISION
)
from dmp_suite.yt.maintenance.merge_compress.merge import merge_and_compress_partition
from dmp_suite.yt import YTTable, YTMeta, Int, etl, operation as op
from dmp_suite.yt import join_path_parts, NotLayeredYtLayout, NotLayeredYtLocation
from dmp_suite.yt.dyntable_operation import operations as dop
from dmp_suite.yt.operation import get_yt_client, read_yt_table, merge_yt_table
from dmp_suite.yt.paths import TAXI_DWH_TEST_PREFIX
from .helpers import is_merge_required_by_attrs, is_compressed


class DynamicTestTable(YTTable):
    __unique_keys__ = True
    __dynamic__ = True

    a = Int(sort_key=True, sort_position=0)
    b = Int()


class DynamicWrongTestTable(YTTable):
    __unique_keys__ = True
    __dynamic__ = True

    b = Int(sort_key=True, sort_position=0)


def _once_random_yt_table():
    """
    Return table modifier that set determinate layout randomize once
    """
    random_name = uuid.uuid4().hex

    new_layout = NotLayeredYtLayout(
        folder=join_path_parts(TAXI_DWH_TEST_PREFIX, random_name),
        name=random_name
    )
    new_location = NotLayeredYtLocation

    def get_table_with_layout(table_cls):
        new_table_cls = type(
            'Random' + table_cls.__name__,
            (table_cls,),
            {
                '__layout__': new_layout,
                '__location_cls__': new_location,
            }
        )
        return new_table_cls
    return get_table_with_layout


_modify_table_table = _once_random_yt_table()


def _fixture_random_yt_table(table_cls: Type[YTTable]):
    """
    Decorator transform YTTable class to pytest fixture. Fixture generate
    subclass __layout__ with random folder and table.
    """
    @pytest.fixture(scope='function')
    def randomized_table_fixture():
        yield _modify_table_table(table_cls)

    return randomized_table_fixture


dynamic_test_table = _fixture_random_yt_table(DynamicTestTable)
dynamic_wrong_test_table = _fixture_random_yt_table(DynamicWrongTestTable)


DEFAULT_ATTRS = [
    'dynamic',
    'compression_codec',
    'erasure_codec',
    'resource_usage',
    DMP_MERGE_CONTENT_REVISION,
    CONTENT_REVISION
]


def get_attrs(meta: YTMeta, attrs: Optional[list] = None):
    if attrs is None:
        attrs = DEFAULT_ATTRS
    return {
        attr_name: op.get_yt_attr(meta, attr_name, default=None)
        for attr_name in attrs
    }


@pytest.mark.slow
def test_just_work(dynamic_test_table):
    """
    Проверяем, что простейшие операции работают
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    attrs = get_attrs(meta)

    PartitionNode(meta, attrs)


@pytest.mark.slow
def test_merge_and_compress_partition(dynamic_test_table):
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    for i in range(3):
        data = [dict(a=j, b=j) for j in range(100 * i, 100 * (i + 1))]
        dop.insert_chunk_in_dynamic_table(meta, data)

        # Сбрасываем данные на диск
        get_yt_client().freeze_table(meta.target_path(), sync=True)
        get_yt_client().unfreeze_table(meta.target_path(), sync=True)

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    assert resource_usage.get('chunk_count') == 3

    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        merge_and_compress_partition(
            PartitionNode(
                meta,
                get_attrs(meta)
            ),
            Pool.RESEARCH
        )

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    assert resource_usage.get('chunk_count') == 1

    # Проверяю, что нет потери данных
    rows = list(read_yt_table(meta.target_path()))
    expected = [dict(a=i, b=i) for i in range(300)]
    assert rows == expected

    # Проверяю, что отработал yt.transform
    assert op.get_yt_attr(meta, 'compression_codec') == 'brotli_8'
    assert op.get_yt_attr(meta, 'erasure_codec') == 'lrc_12_2_2'

    # Проверяю, что установлен аттрибут после мержа
    assert op.get_yt_attr(meta, DMP_MERGE_CONTENT_REVISION) is not None
    assert isinstance(get_dmp_content_revision(meta), int)


@pytest.mark.slow
def test_merge_and_compress_partition2(dynamic_test_table):
    """
    Проверяем, что нет потерь данных
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    # Запишем всего одну строчку
    data = [dict(a=1, b=1)]
    dop.insert_chunk_in_dynamic_table(meta, data)
    # Но не будем сбрасывать данные на диск!

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    # Количество чанков:
    #   0, если данные все еще только в памяти
    #   1, если данные сбросились на диск
    assert 0 <= resource_usage.get('chunk_count') <= 1

    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    # После выполнения merge
    assert resource_usage.get('chunk_count') == 1

    # Проверяю, что нет потери данных
    rows = list(read_yt_table(meta.target_path()))
    assert rows == data

    # Проверяю, что отработал yt.transform
    assert op.get_yt_attr(meta, 'compression_codec') == 'brotli_8'
    assert op.get_yt_attr(meta, 'erasure_codec') == 'lrc_12_2_2'

    # Проверяю, что установлен аттрибут после мержа
    assert op.get_yt_attr(meta, DMP_MERGE_CONTENT_REVISION) is not None
    assert isinstance(get_dmp_content_revision(meta), int)


@pytest.mark.slow
def test_merge_and_compress_partition_is_idempotent(dynamic_test_table):
    """
    Проверяем идемпотентность функции
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    # Вставим данные
    data = [dict(a=1, b=1)]
    dop.insert_chunk_in_dynamic_table(meta, data)

    # Должен требоваться мерж
    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, 0)

    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    dmp_content_revision1 = get_dmp_content_revision(meta)
    content_revision1 = get_content_revision(meta)
    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }

    assert not is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))
    assert is_compressed(actual_attrs)

    # Проверяем постинвариант
    assert content_revision1 == dmp_content_revision1

    # Можно запустить второй раз
    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )
    dmp_content_revision2 = get_dmp_content_revision(meta)
    content_revision2 = get_content_revision(meta)

    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }

    assert not is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))
    assert is_compressed(actual_attrs)

    assert dmp_content_revision1 == dmp_content_revision2
    assert content_revision1 == content_revision2

    # Проверяем, что не продолбали данные
    rows = list(read_yt_table(meta.target_path()))
    assert rows == data


@pytest.mark.slow
def test_unmounted_table(dynamic_test_table):
    """
    Пусть таблиа была отмантирована
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    # Вставим данные
    data = [dict(a=1, b=1)]
    dop.insert_chunk_in_dynamic_table(meta, data)

    dop.unmount_table(meta.target_path(), sync=True)

    # Должен требоваться мерж
    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, 0)

    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }
    assert not is_compressed(actual_attrs)

    # Ожидается только сжатие
    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    # Merge произошел
    assert 0 < get_dmp_content_revision(meta)

    # Compress произошел
    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }
    assert is_compressed(actual_attrs)

    # Проверяем, что не продолбали данные
    rows = list(read_yt_table(meta.target_path()))
    assert rows == data


@pytest.mark.slow
def test_compress_after_merge(dynamic_test_table):
    """
    Пусть таблиа была пожата, но не была помержена
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    # Вставим данные
    data = [dict(a=1, b=1)]
    dop.insert_chunk_in_dynamic_table(meta, data)

    dop.unmount_table(meta.target_path(), sync=True)

    # Сделаем мерж и сжатие
    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    # Сейчас не требуется мерж
    assert not is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))

    # Требуется мерж
    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, 0)
    assert is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))

    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    assert not is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))

    # И теперь табличка осталась сжатой!
    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }
    assert is_compressed(actual_attrs)

    # Проверяем, что не продолбали данные
    rows = list(read_yt_table(meta.target_path()))
    assert rows == data


@pytest.mark.slow
def test_static_table(dynamic_test_table):
    """
    Проверяем, что со статическими таблицами тоже справляемся
    """
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    # Вставим данные
    data = [dict(a=1, b=1)]
    dop.insert_chunk_in_dynamic_table(meta, data)

    # Unmount
    dop.unmount_table(meta.target_path(), sync=True)

    # В статику
    etl.init_rotation_table(meta)
    merge_yt_table(meta.target_path(), meta.rotation_path(), get_pool_value(Pool.RESEARCH), mode='ordered')
    etl.rotation_to_target(meta)

    # А теперь тестируем
    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    # Merge произошел, проверяем постинвариант
    assert get_dmp_content_revision(meta) == get_content_revision(meta)

    # Compress произошел
    actual_attrs = {
        'compression_codec': op.get_yt_attr(meta, 'compression_codec'),
        'erasure_codec': op.get_yt_attr(meta, 'erasure_codec'),
    }
    assert is_compressed(actual_attrs)

    # Проверяем, что не продолбали данные
    rows = list(read_yt_table(meta.target_path()))
    assert rows == data


@pytest.mark.slow
def test_wrong_meta(dynamic_test_table, dynamic_wrong_test_table):
    # Тест по мотивам DMPDEV-4267 "Брать схему из кипариса для MergeAndCompressRawHistTask"
    meta = YTMeta(dynamic_test_table)
    wrong_meta = YTMeta(dynamic_wrong_test_table)

    etl.init_target_table(meta)

    for i in range(3):
        data = [dict(a=j, b=j) for j in range(100 * i, 100 * (i + 1))]
        dop.insert_chunk_in_dynamic_table(meta, data)

        # Сбрасываем данные на диск
        get_yt_client().freeze_table(meta.target_path(), sync=True)
        get_yt_client().unfreeze_table(meta.target_path(), sync=True)

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    assert resource_usage.get('chunk_count') == 3

    # Но подсовываем сюда неправильную мету
    with mock.patch('dmp_suite.yt.maintenance.merge_compress.common._log_resources'):
        partition = PartitionNode(meta, get_attrs(meta))
        merge_and_compress_partition(
            partition,
            Pool.RESEARCH
        )

    resource_usage = op.get_yt_attr(meta, 'resource_usage')
    assert resource_usage.get('chunk_count') == 1

    # Проверяю, что нет потери данных
    rows = list(read_yt_table(meta.target_path()))
    expected = [dict(a=i, b=i) for i in range(300)]
    assert rows == expected

    # Проверяю, что отработал yt.transform
    assert op.get_yt_attr(meta, 'compression_codec') == 'brotli_8'
    assert op.get_yt_attr(meta, 'erasure_codec') == 'lrc_12_2_2'

    # Проверяю, что установлен аттрибут после мержа
    assert op.get_yt_attr(meta, DMP_MERGE_CONTENT_REVISION) is not None
    assert isinstance(get_dmp_content_revision(meta), int)
