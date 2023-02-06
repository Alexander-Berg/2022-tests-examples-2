import pytest
from unittest import TestCase
from pandas import DataFrame

from connection.yt import get_yt_client
from dmp_suite.yt.helpers import load_snapshot
from dmp_suite.yt.table import YTTable, LayeredLayout, DayPartitionScale, String, Datetime
from dmp_suite.yt.meta import resolve_meta

from dmp_suite.adhoc.yt import write, is_path_exists, ls as _ls
from dmp_suite.yt.backup import BackupMode, backup, restore, _make_backup_path


def test_backup_path_should_remove_prefix():
    result = _make_backup_path(
        'root_etl',
        'TAXIDWH-100500',
        '//dummy/ods/some-table/2021-01-01',
    )
    assert result == '//dummy/backup/TAXIDWH-100500/ods/some-table/2021-01-01'


def ls(path):
    names = [path.split('/')[-1] for path in _ls(path)['name']]
    names.sort()
    return names


class TheTable(YTTable):
    __layout__ = LayeredLayout('raw', 'the-table')
    name = String(sort_key=True)


class SingleTableTests(TestCase):
    def setUp(self):
        df = DataFrame([dict(name='Bob')])
        write(TheTable, df)

        meta = resolve_meta(TheTable)
        self.etl_service = meta.layout_prefix_key
        self.source_path = meta.target_path()

    @pytest.mark.slow
    def test_backup_table(self):
        # Тут надо использовать уникальные тикеты, иначе тесты могут флапать при параллельном
        # запуске, ведь тестовый рандомный префикс задаётся один на весь запуск
        # и у меня (art@) не получилось сходу это изменить, заменив scope
        # фикстур с session на function :(
        paths = backup(self.etl_service, 'TICKET-1', self.source_path, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert is_path_exists(destination)

    @pytest.mark.slow
    def test_backup_table_with_move(self):
        paths = backup(self.etl_service, 'TICKET-2',
                       self.source_path, mode=BackupMode.MoveData, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)

    @pytest.mark.slow
    def test_backup_restore(self):
        paths = backup(self.etl_service, 'TICKET-3',
                       self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)

        paths = restore(self.etl_service, 'TICKET-3',
                        self.source_path, mode=BackupMode.Copy, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert is_path_exists(destination)

        paths = restore(self.etl_service, 'TICKET-3',
                        self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert not is_path_exists(destination)


class PartitionedTable(YTTable):
    __layout__ = LayeredLayout('raw', 'the-table')
    __partition_scale__ = DayPartitionScale('time')

    name = String(sort_key=True)
    time = Datetime()


class PartitionedTableTests(TestCase):
    def setUp(self):
        load_snapshot(
            resolve_meta(PartitionedTable, '2020-01-01'),
            [dict(name='Bob', day='2020-01-01')]
        )
        load_snapshot(
            resolve_meta(PartitionedTable, '2020-01-02'),
            [dict(name='Mary', day='2020-01-02')]
        )

        meta = resolve_meta(TheTable)
        self.etl_service = meta.layout_prefix_key
        self.source_path = meta.target_folder_path

        # создаем документ-пустышку
        get_yt_client().create('document', self.source_path + '/test_doc', force=True)
        # создаем файл-пустышку
        get_yt_client().create('file', self.source_path + '/test_file', force=True)

    @pytest.mark.slow
    def test_backup_table(self):
        paths = backup(self.etl_service, 'TICKET-4', self.source_path, force=True)

        for source, destination in paths:
            assert is_path_exists(source)
            assert is_path_exists(destination)
            assert ls(destination) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']

    @pytest.mark.slow
    def test_backup_table_with_move(self):
        paths = backup(self.etl_service, 'TICKET-5',
                       self.source_path, mode=BackupMode.MoveData, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert _ls(source).empty
            assert is_path_exists(destination)
            assert ls(destination) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']

    @pytest.mark.slow
    def test_backup_table_with_move_move_all(self):
        paths = backup(self.etl_service, 'TICKET-6',
                       self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)
            assert ls(destination) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']

    @pytest.mark.slow
    def test_backup_restore(self):
        paths = backup(self.etl_service, 'TICKET-7',
                       self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)
            assert ls(destination) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']

        paths = restore(self.etl_service, 'TICKET-7',
                        self.source_path, mode=BackupMode.Copy, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert ls(source) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']
            assert is_path_exists(destination)
            assert ls(destination) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']

        paths = restore(self.etl_service, 'TICKET-7',
                        self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert ls(source) == ['2020-01-01', '2020-01-02', 'test_doc', 'test_file']
            assert not is_path_exists(destination)


class DynamicTable(YTTable):
    __layout__ = LayeredLayout('raw', 'the-table')
    __dynamic__ = True
    __unique_keys__ = True
    name = String(sort_key=True)
    time = Datetime()


class DynamicTableTests(TestCase):
    def setUp(self):
        write(DynamicTable, DataFrame([dict(name='Bob', time='2020-01-01')]))

        meta = resolve_meta(DynamicTable)
        self.etl_service = meta.layout_prefix_key
        self.source = meta.target_path()
        self.source_path = self.source

    @pytest.mark.slow
    def test_backup_table(self):
        paths = backup(self.etl_service, 'TICKET-8', self.source_path, force=True)

        for source, destination in paths:
            assert is_path_exists(source)
            assert is_path_exists(destination)
            assert get_yt_client().get_attribute(destination, 'dynamic')

    @pytest.mark.slow
    def test_backup_table_with_move(self):
        paths = backup(self.etl_service, 'TICKET-9',
                       self.source_path, mode=BackupMode.MoveData, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)
            assert get_yt_client().get_attribute(destination, 'dynamic')

    @pytest.mark.slow
    def test_backup_restore(self):
        paths = backup(self.etl_service, 'TICKET-10',
                       self.source_path, mode=BackupMode.Move, force=True)
        for source, destination in paths:
            assert not is_path_exists(source)
            assert is_path_exists(destination)
            assert get_yt_client().get_attribute(destination, 'dynamic')

        paths = restore(self.etl_service, 'TICKET-10',
                        self.source_path, mode=BackupMode.Copy, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert get_yt_client().get_attribute(source, 'dynamic')
            assert get_yt_client().get_attribute(source, attribute='tablet_state') == 'unmounted'
            assert is_path_exists(destination)
            assert get_yt_client().get_attribute(destination, 'dynamic')
            assert get_yt_client().get_attribute(destination, attribute='tablet_state') == 'unmounted'

        paths = restore(self.etl_service, 'TICKET-10',
                        self.source_path, mode=BackupMode.Move,
                        mount_tables=True, force=True)
        for source, destination in paths:
            assert is_path_exists(source)
            assert get_yt_client().get_attribute(source, 'dynamic')
            assert get_yt_client().get_attribute(source, attribute='tablet_state') == 'mounted'
            assert not is_path_exists(destination)
