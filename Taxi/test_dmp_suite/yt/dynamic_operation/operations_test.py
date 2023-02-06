# coding: utf-8
import datetime
import time
from collections import defaultdict

import mock
import pytest

from dmp_suite.yt import (
    operation as yt,
    YTTable,
    String,
    YTMeta,
    etl,
    DayPartitionScale,
    Datetime,
)
from dmp_suite.yt.dyntable_operation import operations as ytd
from test_dmp_suite.yt import utils


class DynamicTestTable(YTTable):
    __unique_keys__ = True

    __dynamic__ = True

    a = String(sort_key=True, sort_position=0)
    b = String()


dynamic_test_table = utils.fixture_random_yt_table(DynamicTestTable)


class StaticTestTable(YTTable):
    a = String()
    b = String()


static_test_table = utils.fixture_random_yt_table(StaticTestTable)


class StaticTestTable(YTTable):
    a = String()
    b = String()


class MountUnmountTestTableWithPartitions(YTTable):
    __partition_scale__ = DayPartitionScale('p')

    __unique_keys__ = True
    __dynamic__ = True

    f = String(sort_key=True)
    p = Datetime()


mount_unmount_test_table_with_partitions = utils.fixture_random_yt_table(
    MountUnmountTestTableWithPartitions)


class MountUnmountTestTableWOPartitions(YTTable):
    __unique_keys__ = True
    __dynamic__ = True

    f = String(sort_key=True)
    a = String()


mount_unmount_test_table_wo_partitions = utils.fixture_random_yt_table(
    MountUnmountTestTableWOPartitions)


class UnmountError(Exception):
    pass


@pytest.mark.slow
def test_select_rows(dynamic_test_table):
    meta = YTMeta(dynamic_test_table)
    etl.init_target_table(meta)

    data = [dict(a='1', b='1'),
            dict(a='2', b='2')]

    ytd.insert_chunk_in_dynamic_table(meta, data)
    assert data == list(ytd.select_rows(meta))
    assert data[:1] == list(ytd.select_rows(meta, where="a = '1'"))
    assert data == list(ytd.select_rows(meta, where="a in ('1', '2')"))


@pytest.mark.slow
def test_is_mounted_is_unmounted(mount_unmount_test_table_with_partitions,
                                 mount_unmount_test_table_wo_partitions):
    # partitioned table
    m1 = YTMeta(mount_unmount_test_table_with_partitions, '2019-01-01')
    m2 = YTMeta(mount_unmount_test_table_with_partitions, '2019-01-02')
    meta = YTMeta(mount_unmount_test_table_with_partitions)
    etl.init_target_table([m1, m2])
    ytd.mount_all_partitions(meta)
    assert ytd.is_table_mounted(meta.target_folder_path)
    assert not ytd.is_table_unmounted(meta.target_folder_path)
    ytd.unmount_table(m1.target_path())
    assert not ytd.is_table_mounted(meta.target_folder_path)
    assert ytd.is_table_unmounted(meta.target_folder_path)
    ytd.mount_table(m1.target_path())
    assert ytd.is_table_mounted(meta.target_folder_path)
    assert not ytd.is_table_unmounted(meta.target_folder_path)

    # unpartitioned table
    meta = YTMeta(mount_unmount_test_table_wo_partitions)
    etl.init_target_table(meta)
    ytd.mount_all_partitions(meta)
    assert ytd.is_table_mounted(meta.target_path())
    assert not ytd.is_table_unmounted(meta.target_path())
    ytd.unmount_table(meta.target_path())
    assert not ytd.is_table_mounted(meta.target_path())
    assert ytd.is_table_unmounted(meta.target_path())


@pytest.mark.slow
class TestTemporarilyUnmountedTarget(object):

    def test_unmounts_and_mounts(self, dynamic_test_table):
        meta = YTMeta(dynamic_test_table)
        etl.init_target_table(meta)
        target_table = meta.target_path()

        ytd.mount_table(target_table)
        with ytd.temporarily_unmounted_target(meta):
            assert not ytd.is_table_mounted(target_table)
        assert ytd.is_table_mounted(target_table)

    def test_unmounts_alters_and_mounts(self, dynamic_test_table):
        meta = YTMeta(dynamic_test_table)
        etl.init_target_table(meta)
        target_table = meta.target_path()

        ytd.mount_table(target_table)
        with ytd.temporarily_unmounted_target(meta):
            etl.init_rotation_table(meta)
            # Replacing the unmounted target with static rotation.
            yt.rotate_yt_table(meta.target_path(), meta.rotation_path())
        assert ytd.is_table_mounted(target_table)

    def test_unmounts_mounts_and_raises(self, dynamic_test_table):
        meta = YTMeta(dynamic_test_table)
        etl.init_target_table(meta)
        target_table = meta.target_path()

        ytd.mount_table(target_table)
        with pytest.raises(UnmountError):
            with ytd.temporarily_unmounted_target(meta):
                raise UnmountError()
        assert ytd.is_table_mounted(target_table)

    def test_handles_static_tables(self, static_test_table):
        meta = YTMeta(static_test_table)
        etl.init_target_table(meta)
        target_table = meta.target_path()

        with ytd.temporarily_unmounted_target(meta):
            assert not yt.get_yt_attr(meta, "dynamic")
        assert not yt.get_yt_attr(meta, "dynamic")


@pytest.mark.slow
class TestTemporarilyUnmountedAllPartitionsTarget(object):
    def test_unmounts_and_mounts(self, mount_unmount_test_table_with_partitions):
        meta = YTMeta(mount_unmount_test_table_with_partitions)
        m1 = meta.with_partition('2019-01-01')
        m2 = meta.with_partition('2019-02-01')
        m1_path = m1.target_path()
        m2_path = m2.target_path()
        etl.init_target_table(m1)
        etl.init_target_table(m2)

        ytd.mount_table(m1_path)
        ytd.mount_table(m2_path)
        with ytd.temporarily_unmounted_all_partitions(meta):
            assert not ytd.is_table_mounted(m1_path)
            assert not ytd.is_table_mounted(m2_path)

        assert ytd.is_table_mounted(m1_path)
        assert ytd.is_table_mounted(m2_path)

    def test_unmounts_mounts_and_raises(self, dynamic_test_table):
        meta = YTMeta(dynamic_test_table)
        etl.init_target_table(meta)
        target_table = meta.target_path()

        ytd.mount_table(target_table)
        with pytest.raises(UnmountError):
            with ytd.temporarily_unmounted_all_partitions(meta):
                raise UnmountError()
        assert ytd.is_table_mounted(target_table)


@pytest.mark.slow
def test_wait_for_flush_table():
    def unix_timestamp_to_yt_timestamp(unix_ts):
        return unix_ts * ytd.YT_TS_TO_UNIX_TS_FACTOR

    def get_fake_yt_client(dynamic):
        """
        создадим фейковый клиент, который будет возвращать необходимые нам значения атрибута unflushed_timestamp:
            - 1 й раз timestamp в формате yt в прошлом
            - 2 й раз timestamp в формате yt с текущим временем

        плюс подсчитывает количество вызовов
        """

        called_history = defaultdict(int)
        attributes = iter((unix_timestamp_to_yt_timestamp(before), unix_timestamp_to_yt_timestamp(wait_for + 1)))

        def fake_yt_getter(path, name):
            fake_yt_getter.called = getattr(fake_yt_getter, 'called', called_history)
            fake_yt_getter.called[name] += 1
            if name == 'unflushed_timestamp':
                return next(attributes)
            elif name == 'dynamic':
                return dynamic

        yt_client = mock.MagicMock()
        yt_client.get_attribute = fake_yt_getter
        return yt_client

    # проверка для динамической таблицы
    # мокаем поведение yt и проверяем, что скрипт ожидает когда значение атрибута 'unflushed_timestamp' обгонит время
    # wait_for
    wait_for = time.time()
    before = wait_for - 10  # sec

    fake_yt_client = get_fake_yt_client(dynamic=True)

    with mock.patch('dmp_suite.yt.dyntable_operation.operations.get_yt_client', return_value=fake_yt_client):
        st = time.time()
        ytd._wait_for_flush_table_by_path(
            'fake_yt_path',
            datetime.datetime.utcfromtimestamp(wait_for),
            sleep_time_sec=1,
            wait_time_sec=10,
        )
        perform_time = time.time() - st
        # проверим что атрибут запрашивался 2 раза через фейковый клиент
        assert fake_yt_client.get_attribute.called['unflushed_timestamp'] == 2
        # проверим что было ожидание в 1 секунду
        assert perform_time > 1

    # проверка для статической таблицы
    fake_yt_client = get_fake_yt_client(dynamic=False)
    with mock.patch('dmp_suite.yt.dyntable_operation.operations.get_yt_client', return_value=fake_yt_client):
        ytd._wait_for_flush_table_by_path(
            'fake_yt_path',
            datetime.datetime.utcfromtimestamp(time.time()) # любое значение
        )
        # проверим что атрибут unflushed_timestamp не запрашивался
        assert fake_yt_client.get_attribute.called['unflushed_timestamp'] == 0
